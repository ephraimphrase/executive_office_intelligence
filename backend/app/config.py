from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application
    app_name: str = "EOIS"
    app_env: str = "development"
    debug: bool = True
    secret_key: str
    allowed_origins: str = "http://localhost:3000,http://localhost:3001"

    # Database
    database_url: str
    database_url_sync: str

    # Redis
    redis_url: str
    celery_broker_url: str
    celery_result_backend: str

    # Microsoft Azure / Entra ID
    azure_client_id: str | None = None
    azure_client_secret: str | None = None
    azure_tenant_id: str | None = None
    azure_authority: str | None = None
    ms_graph_endpoint: str = "https://graph.microsoft.com/v1.0"
    ms_graph_scopes: str = "https://graph.microsoft.com/.default"

    # OpenAI
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o"
    openai_embedding_model: str = "text-embedding-3-large"

    # Azure AI Search (Vector DB)
    azure_search_endpoint: str | None = None
    azure_search_key: str | None = None
    azure_search_index: str = "eois-documents"

    # Azure Blob Storage
    azure_storage_connection_string: str | None = None
    azure_storage_container: str = "eois-documents"

    # WhatsApp Business (Meta)
    whatsapp_phone_number_id: str | None = None
    whatsapp_access_token: str | None = None
    whatsapp_verify_token: str | None = None
    whatsapp_api_version: str = "v20.0"

    # Weather API
    openweather_api_key: str | None = None
    gvp_location_lat: float = 6.5244
    gvp_location_lon: float = 3.3792
    gvp_location_name: str = "Lagos"

    # Briefing Generation
    briefing_generation_hour: int = 6
    briefing_generation_minute: int = 0
    briefing_timezone: str = "Africa/Lagos"

    # JWT
    jwt_algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 7

    # Email Polling
    email_poll_interval_seconds: int = 300
    calendar_sync_interval_seconds: int = 600
    onedrive_sync_interval_seconds: int = 1800

    # GVP Configuration
    gvp_email: str = "gvp@dangote.com"
    gvp_name: str = "Group Vice President"
    gvp_timezone: str = "Africa/Lagos"

    model_config = SettingsConfigDict(env_file='.env', case_sensitive=False, extra='ignore')

    @property
    def cors_origins(self) -> list[str]:
        return [origin.strip() for origin in self.allowed_origins.split(',')]

    @property
    def microsoft_graph_enabled(self) -> bool:
        return bool(self.azure_client_id and self.azure_client_secret)

    @property
    def openai_enabled(self) -> bool:
        return bool(self.openai_api_key)

    @property
    def azure_search_enabled(self) -> bool:
        return bool(self.azure_search_endpoint and self.azure_search_key)


@lru_cache
def get_settings() -> Settings:
    return Settings()
