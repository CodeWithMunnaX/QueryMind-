"""Pydantic schemas for the chat/NL2SQL API."""
from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.analytics import ChartConfig


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, max_length=2000)
    conversation_id: str = Field(..., min_length=1, max_length=100)


class ChatMetadata(BaseModel):
    status: Literal["ok", "clarification_needed", "unanswerable", "error"]
    execution_ms: float | None = None
    row_count: int | None = None


class ChatResponse(BaseModel):
    answer: str
    sql: str | None = None
    data: list[dict[str, Any]] = Field(default_factory=list)
    columns: list[str] = Field(default_factory=list)
    chart: ChartConfig | None = None
    metadata: ChatMetadata
    clarification_options: list[str] | None = None


class HistoryItem(BaseModel):
    id: int
    conversation_id: str
    question: str
    sql: str | None = None
    answer: str | None = None
    chart_type: str | None = None
    status: str
    created_at: str


class HistoryResponse(BaseModel):
    items: list[HistoryItem]
