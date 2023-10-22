import logging
from dataclasses import dataclass

from environs import Env
from marshmallow.validate import Length, OneOf
from sqlalchemy.engine import URL

env = Env()
env.read_env()


class DatabaseConfig:
    """Database connection variables"""

    with env.prefixed("POSTGRES_"):
        name: str = env.str("DATABASE", validate=Length(min=1))
        user: str = env("USER", validate=Length(min=1))
        passwd: str = env("PASSWORD", validate=Length(min=1))
        port: int = env.int("PORT", 5432)
        host: str = env("HOST", "db", validate=Length(min=1))

    driver: str = "asyncpg"
    database_system: str = "postgresql"

    def build_connection_str(self) -> str:
        """
        This function build a connection string
        """
        return URL.create(
            drivername=f"{self.database_system}+{self.driver}",
            username=self.user,
            database=self.name,
            password=self.passwd,
            port=self.port,
            host=self.host,
        ).render_as_string(hide_password=False)


class RedisConfig:
    """Redis connection variables"""

    with env.prefixed("REDIS_"):
        db: str = env.int("DATABASE", 1)
        host: str = env("HOST", "redis", validate=Length(min=1))
        port: int = env.int("PORT", 6379)
        passwd: str = env("PASSWORD", validate=Length(min=1))
        username: str = env("USERNAME", None)
        state_ttl: int = env.int("TTL_STATE", None)
        data_ttl: int = env.int("TTL_DATA", None)


@dataclass
class BotConfig:
    """Bot configuration"""

    token: str = env("BOT_TOKEN", validate=Length(min=1))
    admin_list = [x.lower() for x in env.list("ADMIN_LIST", [])]

    announcement_timeout = env.int("ANNOUNCE_TIMEOUT", 30)  # TODO Move setting to DB


class WebConfig:
    """Web configuration"""

    with env.prefixed("WEB_"):
        host: str = env("HOST", "127.0.0.1")
        port: int = env.int("PORT", 8090)
        secret_key: str = env("SECRET_KEY", "a_super_secret_key123")
        mode: str = env("MODE", "polling", validate=OneOf(["polling", "webhook"]))
        domain: str = env("DOMAIN", None)

    def build_webhook_url(self) -> str:
        return f"https://{self.domain}/webhook"

    def build_admin_auth_url(self) -> str:
        if self.domain:
            return f"https://{self.domain}/auth"
        else:
            return f"http://127.0.0.1:{self.port}/auth"


@dataclass
class Configuration:
    """All in one configuration's class"""

    debug = env.bool("DEBUG", False)
    logging_level = env.int("LOGGING_LEVEL", logging.INFO)
    db_echo = env.bool("DB_ECHO", False)
    with env.prefixed("SENTRY_"):
        sentry_enabled = env.bool("ENABLED", False)
        sentry_dsn: str = env("DSN", None)
        sentry_env: str = env("ENV", None)

    db = DatabaseConfig()
    redis = RedisConfig()
    bot = BotConfig()
    web = WebConfig()


conf = Configuration()
