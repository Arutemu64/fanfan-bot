import enum
import logging
from typing import Self

from pydantic import (
    BaseModel,
    DirectoryPath,
    HttpUrl,
    NatsDsn,
    PostgresDsn,
    RedisDsn,
    SecretStr,
    model_validator,
)
from pydantic_extra_types.timezone_name import TimeZoneName
from pydantic_settings import BaseSettings, SettingsConfigDict


class BotMode(enum.StrEnum):
    POLLING = "polling"
    WEBHOOK = "webhook"


class WebhookConfig(BaseModel):
    host: str
    port: int

    base_url: HttpUrl
    path: str = "/webhook"

    def build_webhook_url(self) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme=self.base_url.scheme,
            host=self.base_url.host,
            path=self.path.lstrip("/"),
        )
        return url.unicode_string()


class BotConfig(BaseModel):
    token: SecretStr
    mode: BotMode = BotMode.POLLING

    webhook: WebhookConfig | None = None

    @model_validator(mode="after")
    def check_if_webhook_config_set(self) -> Self:
        if self.mode is BotMode.WEBHOOK and self.webhook is None:
            msg = "Webhook config is not set!"
            raise AssertionError(msg)
        return self


class DatabaseConfig(BaseModel):
    host: str
    port: int
    user: str
    password: SecretStr
    name: str

    database_system: str = "postgresql"
    driver: str = "psycopg"
    echo: bool = True

    def build_connection_str(self) -> str:
        dsn: PostgresDsn = PostgresDsn.build(
            scheme=f"{self.database_system}+{self.driver}",
            username=self.user,
            password=self.password.get_secret_value(),
            host=self.host,
            port=self.port,
            path=self.name,
        )
        return dsn.unicode_string()


class RedisConfig(BaseModel):
    host: str
    port: int
    database: str = "0"
    username: str | None = None
    password: SecretStr | None = None
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


class NatsConfig(BaseModel):
    host: str
    port: int
    user: str
    password: SecretStr

    def build_connection_str(self) -> str:
        dsn: NatsDsn = NatsDsn.build(
            scheme="nats",
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password.get_secret_value(),
        )
        return dsn.unicode_string()


class WebConfig(BaseModel):
    host: str
    port: int

    base_url: HttpUrl
    path: str = "/web"
    secret_key: SecretStr

    def build_admin_auth_url(self, token: str) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme=self.base_url.scheme,
            host=self.base_url.host,
            path=f"{self.path.lstrip('/')}/admin/auth?token={token}",
        )
        return url.unicode_string()

    def build_qr_scanner_url(self) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme=self.base_url.scheme,
            host=self.base_url.host,
            path=f"{self.path.lstrip('/')}/qr_scanner",
        )
        return url.unicode_string()


class DebugConfig(BaseModel):
    enabled: bool = True
    test_mode: bool = False

    logging_level: int = logging.DEBUG
    json_logs: bool = False

    logfire_token: SecretStr | None = None


class TimepadConfig(BaseModel):
    client_id: SecretStr
    event_id: int
    secret: SecretStr


class Cosplay2Config(BaseModel):
    subdomain: str
    login: str
    password: SecretStr

    def build_api_base_url(self) -> str:
        return f"https://{self.subdomain}.cosplay2.ru/api/"


class LimitsConfig(BaseModel):
    announcement_timeout: int = 10


class Configuration(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    env: str
    timezone: TimeZoneName = "Europe/Moscow"
    media_root: DirectoryPath
    docs_link: HttpUrl | None = None

    bot: BotConfig
    web: WebConfig

    db: DatabaseConfig
    redis: RedisConfig
    nats: NatsConfig

    limits: LimitsConfig
    debug: DebugConfig

    timepad: TimepadConfig | None = None
    cosplay2: Cosplay2Config | None = None
