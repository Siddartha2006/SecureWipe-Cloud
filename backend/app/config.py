from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    database_url: str = "postgresql+psycopg://securewipe:securewipe@postgres:5432/securewipe"
    redis_url: str = "redis://redis:6379/0"
    openai_api_key: str = ""
    storage_endpoint: str = ""
    storage_region: str = "us-east-1"
    storage_bucket: str = ""
    storage_access_key: str = ""
    storage_secret_key: str = ""
    verify_base_url: str = "http://localhost:3000"
    certificate_private_key: str = ""
    public_verification_key: str = ""
    jwt_secret: str = "change-me-before-deployment"
    upload_max_bytes: int = 25 * 1024 * 1024
    retention_hours: int = 24
    allowed_origins: str = "http://localhost:3000"


settings = Settings()
