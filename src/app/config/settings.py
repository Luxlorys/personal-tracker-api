"""Runtime configuration.

Configuration is an infrastructure concern: only the `adapters` and `drivers`
layers may import this module. `import-linter` enforces that (see pyproject.toml).
"""

from enum import StrEnum
from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Environment(StrEnum):
    local = "local"
    test = "test"
    staging = "staging"
    production = "production"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Personal Tracker API"
    env: Environment = Environment.local
    log_level: str = "INFO"

    db_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/tracker"
    db_echo: bool = False

    redis_url: str = "redis://localhost:6379/0"

    cors_origins: list[str] = Field(default_factory=lambda: ["http://localhost:3000"])

    @property
    def is_local(self) -> bool:
        return self.env is Environment.local


@lru_cache
def get_settings() -> Settings:
    return Settings()
