import logging

from app.config import get_settings

logger = logging.getLogger(__name__)


class AzureBlobClient:
    """Thin wrapper around Azure Blob Storage. Falls back to local disk (the
    router handles the actual fallback) when no connection string is configured,
    matching the mock/real pattern used by the other integrations in this app."""

    def __init__(self):
        settings = get_settings()
        self.connection_string = settings.azure_storage_connection_string
        self.container_name = settings.azure_storage_container
        self.use_mock = not bool(self.connection_string)

        if self.use_mock:
            logger.info("Azure Blob Storage not configured; documents will be stored on local disk.")

    async def upload_file(self, file_bytes: bytes, blob_name: str, content_type: str | None = None) -> str:
        """Upload bytes to blob storage. Returns the blob name to store for later
        lookup, or "" if blob storage isn't configured (caller should fall back)."""
        if self.use_mock:
            return ""

        from azure.storage.blob.aio import BlobServiceClient

        async with BlobServiceClient.from_connection_string(self.connection_string) as service:
            container = service.get_container_client(self.container_name)
            try:
                await container.create_container()
            except Exception:
                pass  # already exists
            blob_client = container.get_blob_client(blob_name)
            await blob_client.upload_blob(file_bytes, overwrite=True, content_type=content_type)
            return blob_name

    async def download_file(self, blob_name: str) -> bytes:
        if self.use_mock:
            return b""

        from azure.storage.blob.aio import BlobServiceClient

        try:
            async with BlobServiceClient.from_connection_string(self.connection_string) as service:
                container = service.get_container_client(self.container_name)
                blob_client = container.get_blob_client(blob_name)
                stream = await blob_client.download_blob()
                return await stream.readall()
        except Exception as e:
            logger.warning(f"Blob download failed for {blob_name}: {e}")
            return b""

    async def delete_file(self, blob_name: str) -> bool:
        if self.use_mock:
            return True

        from azure.storage.blob.aio import BlobServiceClient

        try:
            async with BlobServiceClient.from_connection_string(self.connection_string) as service:
                container = service.get_container_client(self.container_name)
                await container.get_blob_client(blob_name).delete_blob()
            return True
        except Exception as e:
            logger.warning(f"Blob delete failed for {blob_name}: {e}")
            return False
