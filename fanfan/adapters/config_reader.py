import logging

from dotenv import find_dotenv, load_dotenv
from pydantic import (
    DirectoryPath,
    HttpUrl,
    NatsDsn,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    model_validator,
)
from pydantic.fields import Field
from pydantic_extra_types.timezone_name import TimeZoneName
from pydantic_settings import (
    BaseSettings,
    SettingsConfigDict,
)

from fanfan.core.enums import BotMode

load_dotenv(find_dotenv(".local-env"))  # For local testing


class BotConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="BOT_")

    token: SecretStr
    mode: BotMode = BotMode.POLLING

    webhook_host: str = "127.0.0.1"
    webhook_port: int = 8080


class DatabaseConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    user: str
    password: SecretStr
    host: str = "db"
    port: int = 5432
    name: str = "fanfan"

    database_system: str = "postgresql"
    driver: str = "psycopg"
    echo: bool = True

    def build_connection_str(self) -> str:
        dsn: PostgresDsn = PostgresDsn.build(
            scheme=f"{self.database_system}+{self.driver}",
            username=self.user,
            password=self.password.get_secret_value() if self.password else None,
            host=self.host,
            port=self.port,
            path=self.name,
        )
        return dsn.unicode_string()


class RedisConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="REDIS_")

    username: str | None = None
    password: SecretStr | None = None
    host: str = "redis"
    port: int = 6379
    database: str = "0"
    state_ttl: int | None = None
    data_ttl: int | None = None

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


class NatsConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="NATS_")

    host: str = "nats"
    port: int = 4222
    user: str
    password: str

    def build_connection_str(self) -> str:
        dsn: NatsDsn = NatsDsn.build(
            scheme="nats",
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password,
        )
        return dsn.unicode_string()


class WebConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="WEB_")

    host: str = "127.0.0.1"
    port: int = 8080
    base_url: HttpUrl = HttpUrl("http://127.0.0.1:8080")
    secret_key: SecretStr = Field("a_super_secret_key123")

    def build_webhook_url(self) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme=self.base_url.scheme,
            host=self.base_url.host,
            path="webhook",
        )
        return url.unicode_string()

    def build_admin_auth_url(self, token: str) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme=self.base_url.scheme,
            host=self.base_url.host,
            path=f"web/admin/auth?token={token}",
        )
        return url.unicode_string()

    def build_qr_scanner_url(self) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme=self.base_url.scheme,
            host=self.base_url.host,
            path="web/qr_scanner",
        )
        return url.unicode_string()


class TimepadConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TIMEPAD_")

    client_id: SecretStr | None = None
    event_id: int | None = None
    secret: SecretStr | None = None


class Cosplay2Config(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="COSPLAY2_")

    subdomain: str | None = None
    login: str | None = None
    password: SecretStr | None = None

    def build_api_base_url(self) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme="https", host=f"{self.subdomain}.cosplay2.ru", path="api/"
        )
        return url.unicode_string()


class DebugConfig(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DEBUG_")

    enabled: bool = True
    logging_level: int = logging.DEBUG
    json_logs: bool = False

    sentry_enabled: bool = False
    sentry_dsn: HttpUrl | None = None

    otlp_endpoint: HttpUrl | None = None

    @model_validator(mode="before")
    def check_if_sentry_dsn_set(cls, data: dict) -> dict:
        if data.get("sentry_enabled") and data.get("sentry_dsn") is None:
            msg = "Sentry DSN is not set!"
            raise AssertionError(msg)
        return data


class Configuration(BaseSettings):
    env: str = Field(alias="ENV_NAME")
    timezone: TimeZoneName = "Europe/Moscow"
    media_root: DirectoryPath

    db: DatabaseConfig = DatabaseConfig()
    redis: RedisConfig = RedisConfig()
    nats: NatsConfig = NatsConfig()
    bot: BotConfig = BotConfig()
    web: WebConfig = WebConfig()
    timepad: TimepadConfig = TimepadConfig()
    debug: DebugConfig = DebugConfig()


def get_config() -> Configuration:
    return Configuration()
