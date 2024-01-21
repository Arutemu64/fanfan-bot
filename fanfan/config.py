import logging
from typing import Any, List, Optional, Tuple, Type

from arq.connections import RedisSettings
from dotenv import find_dotenv, load_dotenv
from pydantic import HttpUrl, PostgresDsn, RedisDsn, SecretStr, model_validator
from pydantic.fields import Field, FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)

from fanfan.common.enums import BotMode

load_dotenv(find_dotenv(".local-env"))


class CustomBotSettingsSource(EnvSettingsSource):
    def prepare_field_value(
        self, field_name: str, field: FieldInfo, value: Any, value_is_complex: bool
    ) -> Any:
        if field_name == "admin_list":
            return [str(x).lower() for x in value.split(",")]
        return value


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_")

    token: SecretStr
    admin_list: List[str]
    docs_link: HttpUrl = "https://example.com"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        dotenv_settings: PydanticBaseSettingsSource,
        file_secret_settings: PydanticBaseSettingsSource,
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        return (CustomBotSettingsSource(settings_cls),)


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="POSTGRES_")

    username: str = Field(alias="POSTGRES_USER")
    password: str
    host: str = "db"
    port: int = 5432
    database: str = Field(alias="POSTGRES_DB")

    driver: str = "asyncpg"
    database_system: str = "postgresql"

    def build_connection_str(self) -> str:
        dsn: PostgresDsn = PostgresDsn.build(
            scheme=f"{self.database_system}+{self.driver}",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.database,
        )
        return dsn.unicode_string()


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    username: Optional[str] = None
    password: Optional[str] = None
    host: str = "redis"
    port: int = 6379
    database: str = "0"
    state_ttl: Optional[int] = None
    data_ttl: Optional[int] = None

    def build_connection_str(self) -> str:
        dsn: RedisDsn = RedisDsn.build(
            scheme="redis",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.database,
        )
        return dsn.unicode_string()

    def get_pool_settings(self) -> RedisSettings:
        return RedisSettings.from_dsn(self.build_connection_str())


class WebConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WEB_")

    mode: BotMode = BotMode.POLLING
    host: str = "127.0.0.1"
    port: int = 8090
    domain: str = "127.0.0.1"
    secret_key: SecretStr = Field("a_super_secret_key123")

    @model_validator(mode="before")
    def check_if_domain_set(cls, data: dict) -> dict:
        if data["mode"] == BotMode.WEBHOOK:
            if data.get("domain"):
                assert len(data["domain"]) > 0, "Domain not set"
            else:
                raise AssertionError("Domain not set")
        return data

    def build_webhook_url(self) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme="https",
            host=self.domain,
            path="webhook",
        )
        return url.unicode_string()

    def build_admin_auth_url(self) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme="https" if self.mode is BotMode.WEBHOOK else "http",
            host=self.domain,
            port=self.port if self.mode is BotMode.POLLING else None,
            path="auth",
        )
        return url.unicode_string()


class SentryConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="SENTRY_")

    enabled: bool = False
    dsn: Optional[HttpUrl] = None
    env: Optional[str] = None


class Configuration(BaseSettings):
    debug: bool = True
    logging_level: int = logging.DEBUG
    db_echo: bool = True

    db: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    bot: BotConfig = BotConfig()
    web: WebConfig = WebConfig()
    sentry: SentryConfig = SentryConfig()


conf = Configuration()
