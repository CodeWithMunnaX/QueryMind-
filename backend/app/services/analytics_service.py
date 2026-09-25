"""Result summarization (LLM) and dashboard aggregate metrics (direct SQL, no LLM)."""
import json
import logging

import pandas as pd
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.prompts.analysis_prompt import ANALYSIS_SYSTEM_PROMPT, ANALYSIS_USER_PROMPT
from app.schemas.analytics import ChartConfig, DashboardMetrics, DashboardResponse
from app.services import chart_service
from app.services.llm_service import LLMError, LLMService
from app.services.query_service import QueryExecutionResult

logger = logging.getLogger(__name__)


def summarize_result(
    llm: LLMService, question: str, result: QueryExecutionResult
) -> tuple[str, ChartConfig]:
    """Asks the LLM to summarize the data and suggest a chart; falls back gracefully on failure."""
    if result.row_count == 0:
        return (
            "No rows matched that question. Try widening the date range or filters.",
            ChartConfig(type="none"),
        )

    sample = result.dataframe.head(20)
    # DataFrame -> JSON-safe records (Decimal/Timestamp aren't natively JSON serializable).
    sample_records = json.loads(sample.to_json(orient="records", date_format="iso"))

    user_prompt = ANALYSIS_USER_PROMPT.format(
        question=question,
        columns=result.columns,
        row_count=result.row_count,
        data_sample=json.dumps(sample_records, indent=2, default=str),
    )

    try:
        parsed = llm.complete_json(ANALYSIS_SYSTEM_PROMPT, user_prompt)
        summary = parsed.get("summary") or _fallback_summary(result)
        chart = chart_service.validate_and_build_chart(
            result.dataframe, parsed.get("chart"), fallback_title=question[:80]
        )
    except LLMError:
        logger.warning("Falling back to heuristic summary/chart after LLM failure", exc_info=True)
        summary = _fallback_summary(result)
        chart = chart_service.heuristic_chart(result.dataframe, question[:80])

    return summary, chart


def _fallback_summary(result: QueryExecutionResult) -> str:
    return f"Returned {result.row_count} row(s) across {len(result.columns)} column(s)."


def get_dashboard_metrics(db: Session) -> DashboardResponse:
    metrics_row = db.execute(
        text(
            """
            SELECT
                COALESCE(SUM(sales), 0) AS total_sales,
                COALESCE(SUM(profit), 0) AS total_profit,
                COUNT(DISTINCT order_id) AS total_orders,
                COUNT(DISTINCT customer_id) AS total_customers
            FROM sales
            """
        )
    ).mappings().first()

    total_orders = metrics_row["total_orders"] or 0
    total_sales = float(metrics_row["total_sales"] or 0)
    avg_order_value = round(total_sales / total_orders, 2) if total_orders else 0.0

    metrics = DashboardMetrics(
        total_sales=total_sales,
        total_profit=float(metrics_row["total_profit"] or 0),
        total_orders=total_orders,
        total_customers=metrics_row["total_customers"] or 0,
        average_order_value=avg_order_value,
    )

    sales_over_time = [
        dict(r)
        for r in db.execute(
            text(
                """
                SELECT date_trunc('month', order_date)::date AS month,
                       SUM(sales) AS total_sales
                FROM sales
                GROUP BY 1
                ORDER BY 1
                """
            )
        ).mappings()
    ]

    sales_by_region = [
        dict(r)
        for r in db.execute(
            text(
                """
                SELECT region, SUM(sales) AS total_sales
                FROM sales
                GROUP BY region
                ORDER BY total_sales DESC
                """
            )
        ).mappings()
    ]

    sales_by_category = [
        dict(r)
        for r in db.execute(
            text(
                """
                SELECT category, SUM(sales) AS total_sales
                FROM sales
                GROUP BY category
                ORDER BY total_sales DESC
                """
            )
        ).mappings()
    ]

    top_products = [
        dict(r)
        for r in db.execute(
            text(
                """
                SELECT product_name, SUM(sales) AS total_sales, SUM(profit) AS total_profit
                FROM sales
                GROUP BY product_name
                ORDER BY total_sales DESC
                LIMIT 10
                """
            )
        ).mappings()
    ]

    return DashboardResponse(
        metrics=metrics,
        sales_over_time=_stringify_dates(sales_over_time),
        sales_by_region=sales_by_region,
        sales_by_category=sales_by_category,
        top_products=top_products,
    )


def _stringify_dates(rows: list[dict]) -> list[dict]:
    out = []
    for row in rows:
        new_row = dict(row)
        for k, v in new_row.items():
            if hasattr(v, "isoformat"):
                new_row[k] = v.isoformat()
        out.append(new_row)
    return out
