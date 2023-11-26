import logging
from dataclasses import dataclass, field
from typing import List, Optional

from arq.connections import RedisSettings
from environs import Env
from marshmallow.validate import OneOf
from pydantic import HttpUrl, RedisDsn, SecretStr
from sqlalchemy.engine import URL

from src.bot.structures import BotMode

env = Env()


@dataclass
class BotConfig:
    token: SecretStr = SecretStr(env("BOT_TOKEN"))
    admin_list: List[str] = field(
        default_factory=lambda: [x.lower() for x in env.list("ADMIN_LIST", [])]
    )


@dataclass
class DatabaseConfig:
    with env.prefixed("POSTGRES_"):
        username: str = env("USERNAME")
        password: str = env("PASSWORD")
        host: str = env("HOST", "db")
        port: int = env.int("PORT", 5432)
        database: str = env("DATABASE")

    driver: str = "asyncpg"
    database_system: str = "postgresql"

    def build_connection_str(self) -> str:
        return URL.create(
            drivername=f"{self.database_system}+{self.driver}",
            username=self.username,
            database=self.database,
            password=self.password,
            port=self.port,
            host=self.host,
        ).render_as_string(hide_password=False)


@dataclass
class RedisConfig:
    with env.prefixed("REDIS_"):
        username: Optional[str] = env("USERNAME", None)
        password: Optional[str] = env("PASSWORD", None)
        host: str = env("HOST", "redis")
        port: int = env.int("PORT", 6379)
        database: str = env.str("DATABASE", "1")
        state_ttl: Optional[int] = env.int("TTL_STATE", None)
        data_ttl: Optional[int] = env.int("TTL_DATA", None)

    def build_connection_str(self) -> str:
        dsn = RedisDsn.build(
            scheme="redis",
            username=self.username,
            password=self.password,
            host=self.host,
            port=self.port,
            path=self.database,
        )
        return str(dsn)

    def get_pool_settings(self) -> RedisSettings:
        return RedisSettings.from_dsn(self.build_connection_str())


@dataclass
class WebConfig:
    with env.prefixed("WEB_"):
        mode: BotMode = BotMode(
            env("MODE", BotMode.POLLING, validate=OneOf([x for x in BotMode]))
        )
        host: str = env("HOST", "127.0.0.1")
        port: int = env.int("PORT", 8090)
        domain: Optional[str] = env("DOMAIN", None)
        secret_key: SecretStr = SecretStr(env("SECRET_KEY", "a_super_secret_key123"))

    def build_webhook_url(self) -> str:
        url = HttpUrl.build(
            scheme="https",
            host=self.domain,
            path="webhook",
        )
        return str(url)

    def build_admin_auth_url(self) -> str:
        url = HttpUrl.build(
            scheme="https" if self.mode is BotMode.WEBHOOK else "http",
            host=self.domain if self.mode is BotMode.WEBHOOK else self.host,
            port=self.port if self.mode is BotMode.POLLING else None,
            path="auth",
        )
        return str(url)


@dataclass
class SentryConfig:
    with env.prefixed("SENTRY_"):
        enabled: bool = env.bool("ENABLED", False)
        dsn: Optional[HttpUrl] = env.str("DSN", None)
        env: Optional[str] = env.str("ENV")


@dataclass
class Configuration:
    debug: bool = env.bool("DEBUG", False)
    logging_level: int = env.int("LOGGING_LEVEL", logging.INFO)
    db_echo: bool = env.bool("DB_ECHO", False)

    db = DatabaseConfig()
    redis = RedisConfig()
    bot = BotConfig()
    web = WebConfig()
    sentry = SentryConfig()


conf = Configuration()
