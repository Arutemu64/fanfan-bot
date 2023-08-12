import logging
from dataclasses import dataclass

from environs import Env
from sqlalchemy.engine import URL

env = Env()


class DatabaseConfig:
    """Database connection variables"""

    name: str = env("POSTGRES_DATABASE")
    user: str = env("POSTGRES_USER", "docker")
    passwd: str = env("POSTGRES_PASSWORD", None)
    port: int = env.int("POSTGRES_PORT", 5432)
    host: str = env("POSTGRES_HOST", "db")

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

    db: str = env.int("REDIS_DATABASE", 1)
    host: str = env("REDIS_HOST", "redis")
    port: int = env.int("REDIS_PORT", 6379)
    passwd: str = env("REDIS_PASSWORD")
    username: str = env("REDIS_USERNAME", None)
    state_ttl: int = env.int("REDIS_TTL_STATE", None)
    data_ttl: int = env.int("REDIS_TTL_DATA", None)


@dataclass
class BotConfig:
    """Bot configuration"""

    token: str = env("BOT_TOKEN")
    mode: str = env("MODE", "polling")

    webhook_domain: str = env("WEBHOOK_DOMAIN")

    sentry_dsn: str = env("SENTRY_DSN")
    sentry_env: str = env("SENTRY_ENV")

    events_per_page = env.int("EVENTS_PER_PAGE", 7)
    participants_per_page = env.int("PARTICIPANTS_PER_PAGE", 5)
    announcement_timeout = env.int("ANNOUNCE_TIMEOUT", 30)


@dataclass
class Configuration:
    """All in one configuration's class"""

    debug = env.bool("DEBUG", False)
    logging_level = env.int("LOGGING_LEVEL", logging.INFO)
    db_echo = env.bool("DB_ECHO", False)

    db = DatabaseConfig()
    bot = BotConfig()
    redis = RedisConfig()


conf = Configuration()
