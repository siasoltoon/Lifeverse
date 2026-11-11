from functools import lru_cache

from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "LifeVerse"
    environment: str = "development"
    database_url: str = "sqlite:///./lifeverse.db"
    log_level: str = "INFO"
    metrics_publish_enabled: bool = False
    metrics_export_enabled: bool = False
    metrics_token: str | None = None
    metrics_publish_interval_seconds: int = 15
    metrics_snapshot_ttl_seconds: int = 60
    worker_heartbeat_stale_after_seconds: int = 60

    @field_validator("database_url")
    @classmethod
    def normalize_postgresql_driver(cls, value: str) -> str:
        if value.startswith("postgres://"):
            return value.replace("postgres://", "postgresql+psycopg://", 1)
        if value.startswith("postgresql://"):
            return value.replace("postgresql://", "postgresql+psycopg://", 1)
        return value

    @field_validator("metrics_token")
    @classmethod
    def normalize_metrics_token(cls, value: str | None) -> str | None:
        if value is None:
            return None
        value = value.strip()
        if not value:
            return None
        if len(value) < 32:
            raise ValueError("metrics token must contain at least 32 characters")
        return value

    @model_validator(mode="after")
    def validate_metrics_settings(self):
        if self.metrics_publish_interval_seconds < 1:
            raise ValueError("metrics publish interval must be positive")
        if self.metrics_snapshot_ttl_seconds < self.metrics_publish_interval_seconds * 2:
            raise ValueError("metrics snapshot TTL must be at least twice the publish interval")
        if self.worker_heartbeat_stale_after_seconds < 1:
            raise ValueError("worker heartbeat stale threshold must be positive")
        if self.metrics_export_enabled and not self.metrics_token:
            raise ValueError("metrics token is required when metrics export is enabled")
        return self

    model_config = SettingsConfigDict(env_prefix="LIFEVERSE_", env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
