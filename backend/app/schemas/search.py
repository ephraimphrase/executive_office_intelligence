from typing import Any

from pydantic import BaseModel


class SearchRequest(BaseModel):
    query: str
    filters: dict[str, Any] | None = None
    limit: int = 10

class SearchResult(BaseModel):
    item_type: str
    item_data: dict[str, Any]
    relevance_score: float
    snippet: str | None = None

class SearchResponse(BaseModel):
    results: list[SearchResult]
    total: int
    query_used: str
