"""Pydantic schemas for analytics/chart/query payloads."""
from typing import Any, Literal

from pydantic import BaseModel, Field

ChartType = Literal["bar", "line", "pie", "scatter", "grouped_bar", "table", "none"]


class ChartConfig(BaseModel):
    type: ChartType = "table"
    x: str | None = None
    y: str | None = None
    series: list[str] | None = None
    title: str = ""


class QueryResult(BaseModel):
    columns: list[str]
    rows: list[dict[str, Any]]
    row_count: int
    truncated: bool = False


class QueryRequest(BaseModel):
    sql: str = Field(..., min_length=1)


class SchemaColumn(BaseModel):
    name: str
    type: str


class SchemaTable(BaseModel):
    name: str
    columns: list[SchemaColumn]


class DatabaseSchema(BaseModel):
    tables: list[SchemaTable]


class DashboardMetrics(BaseModel):
    total_sales: float
    total_profit: float
    total_orders: int
    total_customers: int
    average_order_value: float


class DashboardResponse(BaseModel):
    metrics: DashboardMetrics
    sales_over_time: list[dict[str, Any]]
    sales_by_region: list[dict[str, Any]]
    sales_by_category: list[dict[str, Any]]
    top_products: list[dict[str, Any]]


class Dataset(BaseModel):
    id: str
    name: str
    description: str
    table_name: str
    row_count: int
