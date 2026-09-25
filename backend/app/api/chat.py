"""POST /api/chat — the main NL -> SQL -> execute -> summarize -> chart pipeline."""
import logging
import re

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import ConversationMessage, QueryHistory, User
from app.schemas.chat import ChatMetadata, ChatRequest, ChatResponse
from app.services import analytics_service, sql_generator, sql_validator
from app.services.auth_service import get_current_user
from app.services.llm_service import LLMError, get_llm_service
from app.services.query_service import QueryExecutionError, execute_readonly_query

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["chat"], dependencies=[Depends(get_current_user)])

CONTEXT_TURNS = 6


def _load_context(db: Session, user_id: int, conversation_id: str) -> list[dict]:
    history = (
        db.query(ConversationMessage)
        .filter(ConversationMessage.user_id == user_id, ConversationMessage.conversation_id == conversation_id)
        .order_by(ConversationMessage.created_at.desc())
        .limit(CONTEXT_TURNS)
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in reversed(history)]


def _save_message(
    db: Session, user_id: int, conversation_id: str, role: str, content: str, sql: str | None
) -> None:
    db.add(
        ConversationMessage(
            user_id=user_id, conversation_id=conversation_id, role=role, content=content, sql=sql
        )
    )
    db.commit()


def _log_history(
    db: Session,
    user_id: int,
    conversation_id: str,
    question: str,
    status: str,
    sql: str | None = None,
    answer: str | None = None,
    chart_type: str | None = None,
) -> None:
    db.add(
        QueryHistory(
            user_id=user_id,
            conversation_id=conversation_id,
            question=question,
            sql=sql,
            answer=answer,
            chart_type=chart_type,
            status=status,
        )
    )
    db.commit()


_OPTION_SPLIT_RE = re.compile(r",| or ", re.IGNORECASE)
_OPTION_PHRASE_PATTERNS = (
    r"by (.+?)\?",  # "...by sales, profit, or quantity sold?"
    r"(?:options include|such as|options are)\s*(.+?)[.?]",  # "Options include sales, profit, or quantity."
)


def _extract_clarification_options(message: str) -> list[str] | None:
    """Best-effort parse of a clarifying question's metric list into discrete option strings."""
    for pattern in _OPTION_PHRASE_PATTERNS:
        match = re.search(pattern, message, re.IGNORECASE)
        if not match:
            continue
        candidates = [c.strip().rstrip("?.") for c in _OPTION_SPLIT_RE.split(match.group(1))]
        candidates = [c for c in candidates if c and "another" not in c.lower()]
        if candidates:
            return candidates
    return None


@router.post("/chat", response_model=ChatResponse)
def chat(
    payload: ChatRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
) -> ChatResponse:
    try:
        llm = get_llm_service()
    except LLMError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    user_id = current_user.id
    context = _load_context(db, user_id, payload.conversation_id)
    _save_message(db, user_id, payload.conversation_id, "user", payload.message, None)

    try:
        generation = sql_generator.generate_sql(llm, payload.message, context)
    except LLMError as exc:
        answer = "The AI model is temporarily unavailable. Please try again shortly."
        _log_history(db, user_id, payload.conversation_id, payload.message, status="error", answer=str(exc))
        logger.exception("SQL generation failed")
        raise HTTPException(status_code=502, detail=answer) from exc

    if generation.status == sql_generator.SqlGenerationStatus.NO_SQL:
        answer = f"I couldn't answer that because {generation.message}"
        _save_message(db, user_id, payload.conversation_id, "assistant", answer, None)
        _log_history(db, user_id, payload.conversation_id, payload.message, status="unanswerable", answer=answer)
        return ChatResponse(answer=answer, metadata=ChatMetadata(status="unanswerable"))

    if generation.status == sql_generator.SqlGenerationStatus.CLARIFY:
        answer = generation.message or "Could you clarify your question?"
        _save_message(db, user_id, payload.conversation_id, "assistant", answer, None)
        _log_history(
            db, user_id, payload.conversation_id, payload.message, status="clarification_needed", answer=answer
        )
        return ChatResponse(
            answer=answer,
            metadata=ChatMetadata(status="clarification_needed"),
            clarification_options=_extract_clarification_options(answer),
        )

    validation = sql_validator.validate_sql(generation.sql or "")
    if not validation.is_valid:
        answer = "I generated a query but it failed safety validation, so it was not run: " + "; ".join(
            validation.errors
        )
        _save_message(db, user_id, payload.conversation_id, "assistant", answer, generation.sql)
        _log_history(
            db, user_id, payload.conversation_id, payload.message, status="error", sql=generation.sql, answer=answer
        )
        return ChatResponse(
            answer=answer, sql=generation.sql, metadata=ChatMetadata(status="error")
        )

    try:
        result = execute_readonly_query(db, validation.sql)
    except QueryExecutionError as exc:
        answer = f"I couldn't run that query: {exc}"
        _save_message(db, user_id, payload.conversation_id, "assistant", answer, validation.sql)
        _log_history(
            db, user_id, payload.conversation_id, payload.message, status="error", sql=validation.sql, answer=answer
        )
        return ChatResponse(answer=answer, sql=validation.sql, metadata=ChatMetadata(status="error"))

    summary, chart = analytics_service.summarize_result(llm, payload.message, result)

    _save_message(db, user_id, payload.conversation_id, "assistant", summary, validation.sql)
    _log_history(
        db,
        user_id,
        payload.conversation_id,
        payload.message,
        status="ok",
        sql=validation.sql,
        answer=summary,
        chart_type=chart.type,
    )

    return ChatResponse(
        answer=summary,
        sql=validation.sql,
        data=result.rows,
        columns=result.columns,
        chart=chart,
        metadata=ChatMetadata(status="ok", execution_ms=round(result.execution_ms, 1), row_count=result.row_count),
    )
