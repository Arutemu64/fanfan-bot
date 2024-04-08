import logging
from typing import Any, List, Optional, Tuple, Type

from dotenv import find_dotenv, load_dotenv
from pydantic import (
    DirectoryPath,
    HttpUrl,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    model_validator,
)
from pydantic.fields import Field, FieldInfo
from pydantic_settings import (
    BaseSettings,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)
from pytz import timezone
from pytz.exceptions import UnknownTimeZoneError

from fanfan.common.enums import BotMode

load_dotenv(find_dotenv(".local-env"))


class CustomBotSettingsSource(EnvSettingsSource):
    def prepare_field_value(
        self,
        field_name: str,
        field: FieldInfo,
        value: Any,
        value_is_complex: bool,
    ) -> Any:
        if field_name == "admin_list":
            return [str(x).lower() for x in value.split(",")]
        return value


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_")

    token: SecretStr
    admin_list: List[str]
    timezone: str = "Europe/Moscow"
    media_root: DirectoryPath

    @model_validator(mode="before")
    def check_timezone(cls, data: dict) -> dict:
        try:
            timezone(data.get("timezone"))
        except UnknownTimeZoneError:
            raise AssertionError("Incorrect timezone")
        return data

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
    password: SecretStr
    host: str = "db"
    port: int = 5432
    database: str = Field(alias="POSTGRES_DB")

    driver: str = "asyncpg"
    database_system: str = "postgresql"
    echo: bool = True

    def build_connection_str(self) -> str:
        dsn: PostgresDsn = PostgresDsn.build(
            scheme=f"{self.database_system}+{self.driver}",
            username=self.username,
            password=self.password.get_secret_value() if self.password else None,
            host=self.host,
            port=self.port,
            path=self.database,
        )
        return dsn.unicode_string()


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    username: Optional[str] = None
    password: Optional[SecretStr] = None
    host: str = "redis"
    port: int = 6379
    database: str = "0"
    state_ttl: Optional[int] = None
    data_ttl: Optional[int] = None

    def build_connection_str(self) -> str:
        dsn: RedisDsn = RedisDsn.build(
            scheme="redis",
            username=self.username,
            password=self.password.get_secret_value() if self.password else None,
            host=self.host,
            port=self.port,
            path=self.database,
        )
        return dsn.unicode_string()


class WebConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WEB_")

    mode: BotMode = BotMode.POLLING
    host: str = "127.0.0.1"
    port: int = 8090
    domain: str = "127.0.0.1"
    secret_key: SecretStr = Field("a_super_secret_key123")

    @model_validator(mode="before")
    def check_if_domain_set(cls, data: dict) -> dict:
        if data.get("mode") == BotMode.WEBHOOK:
            if data.get("domain"):
                assert len(data["domain"]) > 0, "Domain not set!"
            else:
                raise AssertionError("Domain not set!")
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


class DebugConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DEBUG_")

    enabled: bool = True
    logging_level: int = logging.DEBUG

    sentry_enabled: bool = False
    sentry_dsn: Optional[HttpUrl] = None
    sentry_env: Optional[str] = "local"

    @model_validator(mode="before")
    def check_if_sentry_dsn_set(cls, data: dict) -> dict:
        if data.get("sentry_enabled"):
            if data.get("sentry_dsn") is None:
                raise AssertionError("Sentry DSN is not set!")
        return data


class Configuration:
    db: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    bot: BotConfig = BotConfig()
    web: WebConfig = WebConfig()
    debug: DebugConfig = DebugConfig()


def get_config() -> Configuration:
    return Configuration()
