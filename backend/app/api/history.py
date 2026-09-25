"""GET /api/history — previously asked questions, for the sidebar query-history panel."""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.config import get_settings
from app.database.connection import get_db
from app.database.models import QueryHistory, User
from app.schemas.chat import HistoryItem, HistoryResponse
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/api", tags=["history"], dependencies=[Depends(get_current_user)])


@router.get("/history", response_model=HistoryResponse)
def get_history(
    conversation_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> HistoryResponse:
    settings = get_settings()
    query = db.query(QueryHistory).filter(QueryHistory.user_id == current_user.id)
    if conversation_id:
        query = query.filter(QueryHistory.conversation_id == conversation_id)
    rows = query.order_by(QueryHistory.created_at.desc()).limit(min(limit, settings.history_limit * 4)).all()

    items = [
        HistoryItem(
            id=r.id,
            conversation_id=r.conversation_id,
            question=r.question,
            sql=r.sql,
            answer=r.answer,
            chart_type=r.chart_type,
            status=r.status,
            created_at=r.created_at.isoformat() if r.created_at else "",
        )
        for r in rows
    ]
    return HistoryResponse(items=items)
