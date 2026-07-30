"""
EOIS FastAPI Application Entry Point
Executive Office Intelligence System
"""
import logging
import time
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse, RedirectResponse

from app.config import get_settings

settings = get_settings()

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger("eois")


# ---------------------------------------------------------------------------
# Lifespan (startup / shutdown)
# ---------------------------------------------------------------------------
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    logger.info("🚀 EOIS API starting up...")
    try:
        from app.database import create_tables, init_db
        await create_tables()
        await init_db()
        logger.info("✅ Database tables created and seeded.")
    except Exception as e:
        logger.error(f"❌ Database initialisation failed: {e}")

    logger.info("✅ EOIS API ready.")
    yield

    logger.info("🛑 EOIS API shutting down.")


# ---------------------------------------------------------------------------
# App factory
# ---------------------------------------------------------------------------
app = FastAPI(
    title="EOIS API",
    version="1.0.0",
    description=(
        "Executive Office Intelligence System — AI-powered Chief of Staff "
        "for the Group Vice President of Dangote Group."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# ---------------------------------------------------------------------------
# Middleware
# ---------------------------------------------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(GZipMiddleware, minimum_size=1000)


@app.middleware("http")
async def request_timing_middleware(request: Request, call_next):
    start = time.perf_counter()
    response = await call_next(request)
    duration_ms = (time.perf_counter() - start) * 1000
    response.headers["X-Process-Time-Ms"] = f"{duration_ms:.1f}"
    logger.debug(
        f"{request.method} {request.url.path} → {response.status_code} "
        f"({duration_ms:.1f}ms)"
    )
    return response


# ---------------------------------------------------------------------------
# Global exception handler
# ---------------------------------------------------------------------------
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled exception on {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "message": str(exc)},
    )


# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------
from app.routers import (
    audit_logs,
    auth,
    briefings,
    calendar,
    chat,
    commitments,
    decisions,
    documents,
    emails,
    meetings,
    notifications,
    reports,
    risks,
    search,
    tasks,
    teams,
    users,
    whatsapp,
)

app.include_router(auth.router,          prefix="/api/auth",          tags=["Auth"])
app.include_router(audit_logs.router,    prefix="/api/audit-logs",    tags=["Audit Logs"])
app.include_router(users.router,         prefix="/api/users",         tags=["Users"])
app.include_router(calendar.router,      prefix="/api/calendar",      tags=["Calendar"])
app.include_router(emails.router,        prefix="/api/emails",        tags=["Emails"])
app.include_router(tasks.router,         prefix="/api/tasks",         tags=["Tasks"])
app.include_router(documents.router,     prefix="/api/documents",     tags=["Documents"])
app.include_router(decisions.router,     prefix="/api/decisions",     tags=["Decisions"])
app.include_router(commitments.router,   prefix="/api/commitments",   tags=["Commitments"])
app.include_router(risks.router,         prefix="/api/risks",         tags=["Risks"])
app.include_router(meetings.router,      prefix="/api/meetings",      tags=["Meetings"])
app.include_router(briefings.router,     prefix="/api/briefings",     tags=["Briefings"])
app.include_router(search.router,        prefix="/api/search",        tags=["Search"])
app.include_router(chat.router,          prefix="/api/chat",          tags=["Chat"])
app.include_router(notifications.router, prefix="/api/notifications", tags=["Notifications"])
app.include_router(reports.router,       prefix="/api/reports",       tags=["Reports"])
app.include_router(whatsapp.router,      prefix="/api/whatsapp",      tags=["WhatsApp"])
app.include_router(teams.router,         prefix="/api/teams",         tags=["Teams"])


# ---------------------------------------------------------------------------
# System endpoints
# ---------------------------------------------------------------------------
@app.get("/health", tags=["System"], summary="Health check")
async def health_check():
    """Returns API health status and integration availability."""
    return {
        "status": "healthy",
        "version": "1.0.0",
        "environment": settings.app_env,
        "integrations": {
            "microsoft_graph": "enabled" if settings.microsoft_graph_enabled else "mock",
            "openai":          "enabled" if settings.openai_enabled          else "mock",
            "azure_search":    "enabled" if settings.azure_search_enabled    else "fallback",
            "whatsapp":        "enabled" if settings.whatsapp_access_token   else "mock",
        },
    }


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/docs")
