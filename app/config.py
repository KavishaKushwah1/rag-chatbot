from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    qdrant_url: str = "http://localhost:6333"
    qdrant_api_key: str | None = None

    gemini_api_key: str | None = None

    supabase_url: str | None = None
    supabase_anon_key: str | None = None
    supabase_service_role_key: str | None = None

    langfuse_public_key: str | None = None
    langfuse_secret_key: str | None = None

    embedding_model: str = "BAAI/bge-small-en-v1.5"
    chunk_size: int = 500
    chunk_overlap: int = 75


settings = Settings()