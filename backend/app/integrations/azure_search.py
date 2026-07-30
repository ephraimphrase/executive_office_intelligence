import logging
from typing import Any

import httpx

from app.config import get_settings

logger = logging.getLogger(__name__)

_API_VERSION = "2023-11-01"


class AzureSearchClient:
    def __init__(self):
        settings = get_settings()
        self.endpoint = settings.azure_search_endpoint
        self.api_key = settings.azure_search_key
        self.index_name = settings.azure_search_index
        self.use_mock = not bool(self.endpoint and self.api_key)

        if self.use_mock:
            logger.info("Azure Search credentials not set, using mock/in-memory fallback.")
            self._mock_store = {}

    def _headers(self) -> dict:
        return {"Content-Type": "application/json", "api-key": self.api_key}

    async def index_document(self, doc_id: str, content: str, metadata: dict[str, Any], vector: list[float]) -> bool:
        if self.use_mock:
            self._mock_store[doc_id] = {
                "doc_id": doc_id,
                "content": content,
                "metadata": metadata,
                "vector": vector
            }
            return True

        await self.create_index_if_not_exists()
        url = f"{self.endpoint}/indexes/{self.index_name}/docs/index?api-version={_API_VERSION}"
        payload = {"value": [{
            "@search.action": "mergeOrUpload",
            "id": doc_id,
            "content": content,
            "metadata": str(metadata),
        }]}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=self._headers(), json=payload)
                response.raise_for_status()
            logger.info(f"Indexed document {doc_id} to Azure Search {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"Azure Search index_document failed: {e}")
            return False

    async def search(self, query: str, top_k: int = 5, filter_expr: str | None = None) -> list[dict[str, Any]]:
        if self.use_mock:
            results = []
            for item in list(self._mock_store.values())[:top_k]:
                if query.lower() in item["content"].lower():
                    results.append(item)
            if not results and self._mock_store:
                results = list(self._mock_store.values())[:top_k]
            return results

        url = f"{self.endpoint}/indexes/{self.index_name}/docs/search?api-version={_API_VERSION}"
        payload: dict[str, Any] = {"search": query, "top": top_k}
        if filter_expr:
            payload["filter"] = filter_expr
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=self._headers(), json=payload)
                response.raise_for_status()
                hits = response.json().get("value", [])
            return [
                {"doc_id": h.get("id"), "content": h.get("content"), "metadata": h.get("metadata")}
                for h in hits
            ]
        except Exception as e:
            logger.error(f"Azure Search query failed: {e}")
            return []

    async def delete_document(self, doc_id: str) -> bool:
        if self.use_mock:
            if doc_id in self._mock_store:
                del self._mock_store[doc_id]
            return True

        url = f"{self.endpoint}/indexes/{self.index_name}/docs/index?api-version={_API_VERSION}"
        payload = {"value": [{"@search.action": "delete", "id": doc_id}]}
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(url, headers=self._headers(), json=payload)
                response.raise_for_status()
            logger.info(f"Deleted document {doc_id} from Azure Search")
            return True
        except Exception as e:
            logger.error(f"Azure Search delete_document failed: {e}")
            return False

    async def create_index_if_not_exists(self) -> bool:
        if self.use_mock:
            return True

        check_url = f"{self.endpoint}/indexes/{self.index_name}?api-version={_API_VERSION}"
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(check_url, headers=self._headers())
                if response.status_code == 200:
                    return True

                create_url = f"{self.endpoint}/indexes?api-version={_API_VERSION}"
                schema = {
                    "name": self.index_name,
                    "fields": [
                        {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
                        {"name": "content", "type": "Edm.String", "searchable": True},
                        {"name": "metadata", "type": "Edm.String", "searchable": True},
                    ],
                }
                create_response = await client.post(create_url, headers=self._headers(), json=schema)
                create_response.raise_for_status()
            logger.info(f"Created Azure Search index {self.index_name}")
            return True
        except Exception as e:
            logger.error(f"Azure Search create_index_if_not_exists failed: {e}")
            return False
