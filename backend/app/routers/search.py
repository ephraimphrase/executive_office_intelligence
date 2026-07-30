from typing import Any

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models.user import User
from app.services.search import get_search_suggestions, global_search, semantic_search

router = APIRouter()

@router.get("", response_model=list[dict[str, Any]])
async def search_all(
    q: str = Query(..., min_length=1),
    type: str = Query("all", pattern="^(all|emails|documents|decisions|events|tasks|risks|commitments)$"),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Global search across all entities."""
    results = await global_search(q, type, limit, db)
    return results

@router.post("/semantic", response_model=list[dict[str, Any]])
async def search_semantic(
    query_data: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Semantic vector search for documents."""
    q = query_data.get("q", "")
    limit = query_data.get("limit", 10)
    results = await semantic_search(q, limit, db)
    return results

@router.get("/suggestions", response_model=list[str])
async def search_suggestions(
    q: str = Query(..., min_length=2),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Any:
    """Autocomplete suggestions for search."""
    suggestions = await get_search_suggestions(q, db)
    return suggestions
