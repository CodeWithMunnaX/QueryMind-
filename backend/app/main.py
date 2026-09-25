"""FastAPI application entrypoint."""
import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api import auth, chat, dashboard, history, query, schema
from app.config import get_settings
from app.database.connection import check_connection

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

app = FastAPI(
    title="QueryMind API",
    description="Chat-with-your-data analytics API: NL -> SQL -> execution -> insight -> chart.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(chat.router)
app.include_router(dashboard.router)
app.include_router(schema.router)
app.include_router(history.router)
app.include_router(query.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    # Never leak stack traces / internal details to the client (section 21 of the spec).
    logger.exception("Unhandled exception on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "An unexpected error occurred. Please try again."},
    )


@app.get("/api/health")
def health() -> dict:
    db_ok = check_connection()
    llm_configured = bool(settings.openai_api_key)
    status = "ok" if db_ok and llm_configured else "degraded"
    return {
        "status": status,
        "database": "connected" if db_ok else "unreachable",
        "llm": "configured" if llm_configured else "missing_api_key",
    }
