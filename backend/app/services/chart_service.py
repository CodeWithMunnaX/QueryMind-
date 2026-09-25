"""Determines and validates chart configuration for a query result.

The LLM may suggest a chart type and column mapping, but this module is the source of truth: it
never lets a chart reference a column that isn't actually in the result set, and it falls back to a
rule-based heuristic if the LLM's suggestion is missing or invalid.
"""
import pandas as pd

from app.schemas.analytics import ChartConfig

_VALID_TYPES = {"bar", "line", "pie", "scatter", "grouped_bar", "table", "none"}


def _is_numeric(df: pd.DataFrame, col: str) -> bool:
    return col in df.columns and pd.api.types.is_numeric_dtype(df[col])


def _is_datelike(df: pd.DataFrame, col: str) -> bool:
    if col not in df.columns:
        return False
    if pd.api.types.is_datetime64_any_dtype(df[col]):
        return True
    sample = df[col].dropna().astype(str).head(5)
    return bool(len(sample)) and all(_looks_like_date(v) for v in sample)


def _looks_like_date(value: str) -> bool:
    try:
        pd.to_datetime(value)
        return True
    except (ValueError, TypeError):
        return False


def heuristic_chart(df: pd.DataFrame, title: str = "") -> ChartConfig:
    if df.empty or len(df.columns) < 1:
        return ChartConfig(type="none", title=title)

    if len(df) == 1 and len(df.columns) <= 2:
        return ChartConfig(type="none", title=title)

    numeric_cols = [c for c in df.columns if _is_numeric(df, c)]
    non_numeric_cols = [c for c in df.columns if c not in numeric_cols]
    date_cols = [c for c in non_numeric_cols if _is_datelike(df, c)]

    if date_cols and numeric_cols:
        return ChartConfig(type="line", x=date_cols[0], y=numeric_cols[0], title=title)

    if non_numeric_cols and len(numeric_cols) >= 2:
        return ChartConfig(
            type="grouped_bar",
            x=non_numeric_cols[0],
            series=numeric_cols,
            title=title,
        )

    if non_numeric_cols and numeric_cols:
        category_col = non_numeric_cols[0]
        distinct = df[category_col].nunique()
        if distinct <= 6:
            return ChartConfig(type="pie", x=category_col, y=numeric_cols[0], title=title)
        return ChartConfig(type="bar", x=category_col, y=numeric_cols[0], title=title)

    if len(numeric_cols) >= 2:
        return ChartConfig(type="scatter", x=numeric_cols[0], y=numeric_cols[1], title=title)

    return ChartConfig(type="table", title=title)


def validate_and_build_chart(
    df: pd.DataFrame, suggested: dict | None, fallback_title: str = ""
) -> ChartConfig:
    """Sanitizes an LLM-suggested chart dict against the actual dataframe, or falls back."""
    if not suggested or not isinstance(suggested, dict):
        return heuristic_chart(df, fallback_title)

    chart_type = suggested.get("type")
    if chart_type not in _VALID_TYPES:
        return heuristic_chart(df, fallback_title)

    x = suggested.get("x")
    y = suggested.get("y")
    series = suggested.get("series")
    title = suggested.get("title") or fallback_title

    columns = set(df.columns)
    if x is not None and x not in columns:
        return heuristic_chart(df, fallback_title)
    if y is not None and y not in columns:
        return heuristic_chart(df, fallback_title)
    if series is not None:
        if not isinstance(series, list) or not all(s in columns for s in series):
            return heuristic_chart(df, fallback_title)

    if chart_type in {"bar", "line", "pie"} and not (x and y):
        return heuristic_chart(df, fallback_title)
    if chart_type == "scatter" and not (x and y):
        return heuristic_chart(df, fallback_title)
    if chart_type == "grouped_bar" and not (x and series):
        return heuristic_chart(df, fallback_title)

    return ChartConfig(type=chart_type, x=x, y=y, series=series, title=title)
