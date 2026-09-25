"""Dynamic database schema introspection.

The rest of the app (SQL generation, validation, hallucination checks) reads the schema from here
rather than hardcoding table/column names, so a schema change only ever needs updating in one place.
"""
from dataclasses import dataclass

from sqlalchemy import inspect

from app.config import get_settings
from app.database.connection import engine
from app.schemas.analytics import DatabaseSchema, SchemaColumn, SchemaTable


@dataclass(frozen=True)
class TableSchema:
    name: str
    columns: dict[str, str]  # column_name -> sql type string


def _fetch_schema() -> dict[str, TableSchema]:
    settings = get_settings()
    inspector = inspect(engine)
    tables: dict[str, TableSchema] = {}
    for table_name in inspector.get_table_names():
        if table_name != settings.allowed_table:
            # Only the analytics table is exposed to the LLM/user; internal app tables
            # (query_history, conversation_messages) are never queryable via chat.
            continue
        columns = {col["name"]: str(col["type"]) for col in inspector.get_columns(table_name)}
        tables[table_name] = TableSchema(name=table_name, columns=columns)
    return tables


# Cached because schema introspection hits the database; cleared via refresh_schema_cache()
# after seeding so the app never runs on a stale view of the table.
_cache: dict[str, TableSchema] | None = None


def get_schema(force_refresh: bool = False) -> dict[str, TableSchema]:
    global _cache
    if _cache is None or force_refresh:
        _cache = _fetch_schema()
    return _cache


def refresh_schema_cache() -> None:
    global _cache
    _cache = None


def get_schema_as_prompt_text() -> str:
    schema = get_schema()
    lines = []
    for table in schema.values():
        lines.append(f"Table: {table.name}")
        for col_name, col_type in table.columns.items():
            lines.append(f"  - {col_name} ({col_type})")
    return "\n".join(lines) if lines else "No tables available."


def get_schema_response() -> DatabaseSchema:
    schema = get_schema()
    return DatabaseSchema(
        tables=[
            SchemaTable(
                name=table.name,
                columns=[SchemaColumn(name=n, type=t) for n, t in table.columns.items()],
            )
            for table in schema.values()
        ]
    )


def is_known_table(table_name: str) -> bool:
    return table_name.lower() in get_schema()


def is_known_column(table_name: str, column_name: str) -> bool:
    table = get_schema().get(table_name.lower())
    return bool(table and column_name.lower() in {c.lower() for c in table.columns})


def all_column_names() -> set[str]:
    names: set[str] = set()
    for table in get_schema().values():
        names.update(c.lower() for c in table.columns)
    return names
