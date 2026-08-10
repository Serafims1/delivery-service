from functools import lru_cache
from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    YamlConfigSettingsSource,
)

ROOT_DIR = Path(__file__).resolve().parents[3]
CONFIG_PATH = ROOT_DIR / "config.yaml"


class AppSettings(BaseModel):
    name: str
    debug: bool = False
    secret_key: str


class ServerSettings(BaseModel):
    host: str = "0.0.0.0"  # nosec B104
    port: int = 8000


class DatabaseSettings(BaseModel):
    host: str
    port: int = 5432
    name: str
    user: str
    password: str


class RedisSettings(BaseModel):
    host: str
    port: int = 6379
    db: int = 0
    exchange_rate_ttl_seconds: int = 300
    idempotency_ttl_seconds: int = 300


class ExchangeRateSettings(BaseModel):
    url: str
    request_timeout_seconds: int = 5


class RabbitMQSettings(BaseModel):
    host: str
    port: int = 5672
    user: str
    password: str


class Settings(BaseSettings):
    app: AppSettings
    server: ServerSettings
    database: DatabaseSettings
    redis: RedisSettings
    exchange_rate: ExchangeRateSettings
    rabbitmq: RabbitMQSettings

    model_config = SettingsConfigDict(
        env_nested_delimiter="__",
        yaml_file=CONFIG_PATH,
        yaml_file_encoding="utf-8",
        extra="forbid",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            init_settings,
            env_settings,
            YamlConfigSettingsSource(settings_cls),
            file_secret_settings,
        )


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
