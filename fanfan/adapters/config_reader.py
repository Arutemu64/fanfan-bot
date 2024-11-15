import logging
import os
import tomllib
from pathlib import Path

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

from fanfan.common.paths import ROOT_DIR
from fanfan.core.enums import BotMode

DEFAULT_CONFIG_PATH = ROOT_DIR.joinpath("config/config.toml")


class WebhookConfig(BaseModel):
    host: str
    port: int


class BotConfig(BaseModel):
    token: SecretStr
    mode: BotMode = BotMode.POLLING

    webhook: WebhookConfig | None = None

    @model_validator(mode="before")
    def check_if_webhook_config_set(cls, data: dict) -> dict:
        if data.get("webhook") and data.get("mode") is BotMode.WEBHOOK:
            msg = "Webhook config is not set!"
            raise AssertionError(msg)
        return data


class WebConfig(BaseModel):
    host: str
    port: int
    base_url: HttpUrl
    secret_key: SecretStr

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
            password=self.password.get_secret_value() if self.password else None,
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


class TimepadConfig(BaseModel):
    client_id: SecretStr
    event_id: int
    secret: SecretStr


class Cosplay2Config(BaseModel):
    subdomain: str
    login: str
    password: SecretStr

    def build_api_base_url(self) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme="https", host=f"{self.subdomain}.cosplay2.ru", path="api/"
        )
        return url.unicode_string()


class DebugConfig(BaseModel):
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


class Configuration(BaseModel):
    env_name: str
    timezone: TimeZoneName = "Europe/Moscow"
    media_root: DirectoryPath

    bot: BotConfig
    web: WebConfig | None = None

    db: DatabaseConfig
    redis: RedisConfig
    nats: NatsConfig

    debug: DebugConfig

    timepad: TimepadConfig | None = None
    cosplay2: Cosplay2Config | None = None


def get_config() -> Configuration:
    # Pick config path
    if config_path := os.getenv("CONFIG_PATH"):
        path = Path(config_path)
    else:
        path = DEFAULT_CONFIG_PATH
    # Load config
    with path.open("rb") as cfg:
        cfg_dict = tomllib.load(cfg)
    # Read additional parameters from env
    cfg_dict.update(env_name=os.getenv("ENV_NAME", default="dev"))
    return Configuration.model_validate(cfg_dict)
