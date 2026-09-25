"""Chart selection/validation tests — pure functions, no network needed."""
import pandas as pd

from app.services.chart_service import heuristic_chart, validate_and_build_chart


def test_time_series_picks_line_chart() -> None:
    df = pd.DataFrame({"month": ["2025-01-01", "2025-02-01", "2025-03-01"], "total_sales": [100, 200, 150]})
    chart = heuristic_chart(df)
    assert chart.type == "line"
    assert chart.x == "month"
    assert chart.y == "total_sales"


def test_category_numeric_picks_bar_chart() -> None:
    df = pd.DataFrame({"region": ["West", "East", "Central", "South", "North", "Mid", "Far", "Near"],
                        "total_sales": [1, 2, 3, 4, 5, 6, 7, 8]})
    chart = heuristic_chart(df)
    assert chart.type == "bar"


def test_small_category_distribution_picks_pie() -> None:
    df = pd.DataFrame({"category": ["Technology", "Furniture", "Office Supplies"], "total_sales": [100, 50, 25]})
    chart = heuristic_chart(df)
    assert chart.type == "pie"


def test_two_numeric_columns_picks_scatter() -> None:
    df = pd.DataFrame({"discount": [0.1, 0.2, 0.3], "profit": [10, 5, -2]})
    chart = heuristic_chart(df)
    assert chart.type == "scatter"


def test_multi_metric_picks_grouped_bar() -> None:
    df = pd.DataFrame({"category": ["Tech", "Furniture"], "total_sales": [100, 50], "total_profit": [20, 5]})
    chart = heuristic_chart(df)
    assert chart.type == "grouped_bar"
    assert set(chart.series) == {"total_sales", "total_profit"}


def test_single_row_returns_none_chart() -> None:
    df = pd.DataFrame({"total_sales": [12345]})
    chart = heuristic_chart(df)
    assert chart.type == "none"


def test_empty_dataframe_returns_none_chart() -> None:
    df = pd.DataFrame()
    chart = heuristic_chart(df)
    assert chart.type == "none"


def test_llm_suggestion_referencing_nonexistent_column_falls_back() -> None:
    df = pd.DataFrame({"region": ["West", "East"], "total_sales": [100, 50]})
    suggested = {"type": "bar", "x": "region", "y": "made_up_column", "title": "t"}
    chart = validate_and_build_chart(df, suggested)
    # Falls back to the heuristic instead of trusting the hallucinated column.
    assert chart.y != "made_up_column"


def test_valid_llm_suggestion_is_used_as_is() -> None:
    df = pd.DataFrame({"region": ["West", "East"], "total_sales": [100, 50]})
    suggested = {"type": "pie", "x": "region", "y": "total_sales", "title": "Sales by Region"}
    chart = validate_and_build_chart(df, suggested)
    assert chart.type == "pie"
    assert chart.title == "Sales by Region"


def test_missing_suggestion_falls_back_to_heuristic() -> None:
    df = pd.DataFrame({"region": ["West", "East", "North"], "total_sales": [100, 50, 25]})
    chart = validate_and_build_chart(df, None, fallback_title="fallback")
    assert chart.type in {"bar", "pie"}
