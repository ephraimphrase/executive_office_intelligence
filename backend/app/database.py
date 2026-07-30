"""
Database setup — async SQLAlchemy engine.
Supports SQLite (local dev) and PostgreSQL (production / Docker).
"""
import logging
import uuid
from collections.abc import AsyncGenerator

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()

# ---------------------------------------------------------------------------
# Engine — SQLite for dev, PostgreSQL for production
# ---------------------------------------------------------------------------
_is_sqlite = settings.database_url.startswith("sqlite")

_engine_kwargs: dict = {"echo": settings.debug}
if not _is_sqlite:
    # PostgreSQL-specific pool settings
    _engine_kwargs.update({"pool_pre_ping": True, "pool_size": 10, "max_overflow": 20})
else:
    # SQLite needs check_same_thread=False
    _engine_kwargs["connect_args"] = {"check_same_thread": False}

async_engine = create_async_engine(settings.database_url, **_engine_kwargs)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)

Base = declarative_base()


# ---------------------------------------------------------------------------
# Dependency
# ---------------------------------------------------------------------------
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """FastAPI dependency that yields an async DB session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except SQLAlchemyError as exc:
            logger.error(f"Database session error: {exc}")
            await session.rollback()
            raise
        finally:
            await session.close()


# ---------------------------------------------------------------------------
# Initialisation helpers
# ---------------------------------------------------------------------------
async def create_tables() -> None:
    """Create all tables defined by SQLAlchemy models."""
    # Import all models so Base.metadata knows about every table
    import app.models  # noqa: F401
    async with async_engine.begin() as conn:
        if not _is_sqlite:
            # Needed for Document.embedding (pgvector semantic search).
            # On Azure Database for PostgreSQL, the server's `azure.extensions`
            # allow-list must include `vector` before this succeeds.
            from sqlalchemy import text
            try:
                await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
            except Exception as e:
                logger.warning(f"Could not ensure pgvector extension (semantic search will be degraded): {e}")
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ All database tables ensured.")


async def init_db() -> None:
    """Seed the database with a default admin user for development."""
    from sqlalchemy.future import select as sa_select

    from app.models.user import User, UserRole

    async with AsyncSessionLocal() as session:
        result = await session.execute(
            sa_select(User).where(User.email == "admin@eois.local")
        )
        admin = result.scalars().first()
        if not admin:
            from app.services.auth import hash_password
            new_admin = User(
                id=uuid.uuid4(),
                email="admin@eois.local",
                full_name="System Administrator",
                hashed_password=hash_password("Admin@EOIS2024!"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(new_admin)
            await session.commit()
            logger.info("✅ Default admin user created → admin@eois.local / Admin@EOIS2024!")
        else:
            logger.info("ℹ️  Admin user already exists, skipping seed.")
