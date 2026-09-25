"""Thin wrapper around the LLM (via LangChain's ChatOpenAI) used by other services.

Keeping all model I/O behind this one class means sql_generator and analytics_service never touch
the OpenAI SDK directly, and API keys never leave the backend process.
"""
import json
import logging

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import get_settings

logger = logging.getLogger(__name__)


class LLMError(Exception):
    """Raised when the LLM call fails or returns something unusable."""


class LLMService:
    def __init__(self) -> None:
        settings = get_settings()
        if not settings.openai_api_key:
            raise LLMError("OPENAI_API_KEY is not configured on the backend.")
        self._llm = ChatOpenAI(
            model=settings.openai_model,
            temperature=settings.openai_temperature,
            api_key=settings.openai_api_key,
            timeout=30,
            max_retries=2,
        )

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        try:
            response = self._llm.invoke(
                [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
            )
        except Exception as exc:  # network/auth/rate-limit errors from the provider
            logger.exception("LLM call failed")
            raise LLMError(f"The AI model call failed: {exc}") from exc

        content = response.content
        if isinstance(content, list):
            content = "".join(str(part) for part in content)
        return (content or "").strip()

    def complete_json(self, system_prompt: str, user_prompt: str) -> dict:
        try:
            json_llm = self._llm.bind(response_format={"type": "json_object"})
            response = json_llm.invoke(
                [SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)]
            )
        except Exception as exc:
            logger.exception("LLM JSON call failed")
            raise LLMError(f"The AI model call failed: {exc}") from exc

        content = response.content
        if isinstance(content, list):
            content = "".join(str(part) for part in content)
        raw = (content or "").strip()

        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            pass

        # Fallback: the model sometimes wraps JSON in prose or fences despite json_object mode.
        # Grab the outermost {...} span and try again before giving up.
        start, end = raw.find("{"), raw.rfind("}")
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(raw[start : end + 1])
            except json.JSONDecodeError:
                pass

        logger.warning("LLM did not return valid JSON: %s", raw[:500])
        raise LLMError("The AI model returned an unparseable response.")


_llm_service: LLMService | None = None


def get_llm_service() -> LLMService:
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMService()
    return _llm_service
