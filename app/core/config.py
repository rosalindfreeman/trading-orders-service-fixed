from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    app_name: str = "Trading Orders API"
    database_url: str = "sqlite+aiosqlite:///./orders.db"
    jwt_secret: str = Field(default="development-secret-change-before-production", min_length=32)
    jwt_issuer: str = "trading-orders"
    jwt_audience: str = "trading-apps"
    token_ttl_seconds: int = Field(default=900, ge=60, le=86400)
    client_id: str = "demo-trader"
    client_secret: str = "demo-secret"
    log_level: str = "INFO"
    db_pool_size: int = Field(default=10, ge=1, le=100)
    db_max_overflow: int = Field(default=20, ge=0, le=100)


@lru_cache
def get_settings() -> Settings:
    return Settings()

