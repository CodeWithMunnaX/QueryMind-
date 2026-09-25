"""SQL safety and schema validation using SQLGlot.

This is the last line of defense before anything the LLM wrote touches PostgreSQL. Every rule here
must fail closed: on any doubt (parse error, unresolvable table/column, disallowed keyword) the
query is rejected rather than executed.
"""
from dataclasses import dataclass, field

import sqlglot
from sqlglot import exp

from app.config import get_settings
from app.services import schema_service

# Statement types that are never allowed, regardless of where they appear in the parse tree.
# Looked up via getattr since not every sqlglot version ships every class name (e.g. TruncateTable).
_FORBIDDEN_EXPRESSION_NAMES = (
    "Insert",
    "Update",
    "Delete",
    "Drop",
    "Alter",
    "Create",
    "TruncateTable",
    "Truncate",
    "Grant",
    "Merge",
    "Command",  # catches things sqlglot can't otherwise classify (e.g. GRANT/REVOKE variants)
)
_FORBIDDEN_EXPRESSIONS = tuple(
    cls for cls in (getattr(exp, name, None) for name in _FORBIDDEN_EXPRESSION_NAMES) if cls is not None
)

# Function calls that can leak data, write to disk, or otherwise escape a read-only query.
_FORBIDDEN_FUNCTIONS = {
    "pg_sleep",
    "pg_read_file",
    "pg_read_binary_file",
    "pg_ls_dir",
    "lo_import",
    "lo_export",
    "dblink",
    "copy",
}


@dataclass
class ValidationResult:
    is_valid: bool
    sql: str = ""
    errors: list[str] = field(default_factory=list)


def _has_forbidden_expression(tree: exp.Expression) -> str | None:
    for node in tree.walk():
        node_expr = node[0] if isinstance(node, tuple) else node
        if isinstance(node_expr, _FORBIDDEN_EXPRESSIONS):
            return type(node_expr).__name__
    return None


def _has_forbidden_function(tree: exp.Expression) -> str | None:
    for func in tree.find_all(exp.Anonymous, exp.Func):
        name = (func.name or "").lower()
        if name in _FORBIDDEN_FUNCTIONS:
            return name
    return None


def _referenced_tables(tree: exp.Expression) -> set[str]:
    return {t.name.lower() for t in tree.find_all(exp.Table) if t.name}


def _referenced_columns(tree: exp.Expression) -> set[str]:
    return {c.name.lower() for c in tree.find_all(exp.Column) if c.name and c.name != "*"}


def _apply_row_limit(tree: exp.Select, max_rows: int) -> exp.Expression:
    """Clamp (or add) a LIMIT so a runaway aggregation-free query can't return unbounded rows."""
    existing_limit = tree.args.get("limit")
    if existing_limit is not None:
        try:
            current = int(existing_limit.expression.this)
            if current > max_rows:
                tree.set("limit", exp.Limit(this=None, expression=exp.Literal.number(max_rows)))
        except (TypeError, ValueError, AttributeError):
            tree.set("limit", exp.Limit(this=None, expression=exp.Literal.number(max_rows)))
    else:
        tree.set("limit", exp.Limit(this=None, expression=exp.Literal.number(max_rows)))
    return tree


def validate_sql(raw_sql: str) -> ValidationResult:
    settings = get_settings()
    errors: list[str] = []

    sql = raw_sql.strip()
    if not sql:
        return ValidationResult(is_valid=False, errors=["Empty SQL statement."])

    # Reject multiple statements up front (sqlglot.parse splits on ';' and yields >1 statement).
    try:
        statements = [s for s in sqlglot.parse(sql, read="postgres") if s is not None]
    except Exception as exc:  # sqlglot raises its own ParseError subclasses
        return ValidationResult(is_valid=False, errors=[f"SQL failed to parse: {exc}"])

    if len(statements) == 0:
        return ValidationResult(is_valid=False, errors=["No SQL statement found."])
    if len(statements) > 1:
        return ValidationResult(is_valid=False, errors=["Multiple SQL statements are not allowed."])

    tree = statements[0]

    if not isinstance(tree, (exp.Select, exp.Union, exp.With)):
        return ValidationResult(
            is_valid=False,
            errors=["Only read-only SELECT/WITH statements are allowed."],
        )

    forbidden = _has_forbidden_expression(tree)
    if forbidden:
        errors.append(f"Statement contains a disallowed operation: {forbidden}.")

    forbidden_fn = _has_forbidden_function(tree)
    if forbidden_fn:
        errors.append(f"Statement calls a disallowed function: {forbidden_fn}().")

    # Schema validation: every referenced table/column must exist in the exposed schema.
    # CTE names (WITH foo AS (...)) are virtual tables the query itself defines, not real ones.
    schema = schema_service.get_schema()
    cte_names = {cte.alias.lower() for cte in tree.find_all(exp.CTE) if cte.alias}
    allowed_tables = set(schema.keys()) | cte_names
    tables = _referenced_tables(tree)
    unknown_tables = tables - allowed_tables
    if unknown_tables:
        errors.append(f"Unknown or unauthorized table(s): {', '.join(sorted(unknown_tables))}.")

    if not unknown_tables and tables:
        allowed_columns = schema_service.all_column_names()
        columns = _referenced_columns(tree)
        # Exclude common aliases the query itself defines (SELECT x AS alias ... ORDER BY alias)
        defined_aliases = {a.alias.lower() for a in tree.find_all(exp.Alias) if a.alias}
        unknown_columns = columns - allowed_columns - defined_aliases
        if unknown_columns:
            errors.append(
                f"Unknown or unauthorized column(s): {', '.join(sorted(unknown_columns))}."
            )

    if errors:
        return ValidationResult(is_valid=False, errors=errors)

    # Enforce a max row cap on the outermost SELECT.
    if isinstance(tree, exp.Select):
        tree = _apply_row_limit(tree, settings.max_result_rows)
    elif isinstance(tree, exp.With) and isinstance(tree.this, exp.Select):
        tree.set("this", _apply_row_limit(tree.this, settings.max_result_rows))

    safe_sql = tree.sql(dialect="postgres")
    return ValidationResult(is_valid=True, sql=safe_sql)
