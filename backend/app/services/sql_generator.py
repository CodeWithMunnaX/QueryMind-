"""Natural language -> SQL generation, including hallucination and ambiguity handling."""
import re
from dataclasses import dataclass
from enum import Enum

from app.prompts.sql_prompt import SQL_SYSTEM_PROMPT, SQL_USER_PROMPT
from app.services import schema_service
from app.services.llm_service import LLMService

_SQL_FENCE_RE = re.compile(r"^```(?:sql)?\s*|\s*```$", re.IGNORECASE | re.MULTILINE)


class SqlGenerationStatus(str, Enum):
    OK = "ok"
    NO_SQL = "no_sql"
    CLARIFY = "clarify"


@dataclass
class SqlGenerationResult:
    status: SqlGenerationStatus
    sql: str | None = None
    message: str | None = None  # populated for NO_SQL / CLARIFY


def _strip_fences(text: str) -> str:
    return _SQL_FENCE_RE.sub("", text).strip()


def generate_sql(
    llm: LLMService,
    question: str,
    conversation_context: list[dict[str, str]] | None = None,
) -> SqlGenerationResult:
    schema_text = schema_service.get_schema_as_prompt_text()
    context_text = "\n".join(
        f"{turn['role']}: {turn['content']}" for turn in (conversation_context or [])
    ) or "(no prior context)"

    system_prompt = SQL_SYSTEM_PROMPT.format(schema=schema_text, context=context_text)
    user_prompt = SQL_USER_PROMPT.format(question=question)

    raw = llm.complete(system_prompt, user_prompt)
    raw = _strip_fences(raw)

    if raw.upper().startswith("NO_SQL:"):
        return SqlGenerationResult(
            status=SqlGenerationStatus.NO_SQL, message=raw.split(":", 1)[1].strip()
        )
    if raw.upper().startswith("CLARIFY:"):
        return SqlGenerationResult(
            status=SqlGenerationStatus.CLARIFY, message=raw.split(":", 1)[1].strip()
        )

    sql = raw.rstrip(";").strip()
    return SqlGenerationResult(status=SqlGenerationStatus.OK, sql=sql)
