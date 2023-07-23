import logging
from dataclasses import dataclass
from os import getenv

from sqlalchemy.engine import URL


class DatabaseConfig:
    """Database connection variables"""

    name: str = getenv("POSTGRES_DATABASE")
    user: str = getenv("POSTGRES_USER", "docker")
    passwd: str = getenv("POSTGRES_PASSWORD", None)
    port: int = int(getenv("POSTGRES_PORT", 5432))
    host: str = getenv("POSTGRES_HOST", "db")

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

    db: str = int(getenv("REDIS_DATABASE", 1))
    host: str = getenv("REDIS_HOST", "redis")
    port: int = int(getenv("REDIS_PORT", 6379))
    passwd: str = getenv("REDIS_PASSWORD")
    username: int = getenv("REDIS_USERNAME")
    state_ttl: int = getenv("REDIS_TTL_STATE", None)
    data_ttl: int = getenv("REDIS_TTL_DATA", None)


@dataclass
class BotConfig:
    """Bot configuration"""

    token: str = getenv("BOT_TOKEN")
    mode: str = getenv("MODE", "polling")

    channel_id = int(getenv("CHANNEL_ID"))
    channel_link = getenv("CHANNEL_LINK")

    ngrok_auth: str = getenv("NGROK_AUTH")
    ngrok_region = getenv("NGROK_REGION", "eu")

    sentry_dsn = getenv("SENTRY_DSN")
    sentry_env = getenv("SENTRY_ENV")


@dataclass
class Configuration:
    """All in one configuration's class"""

    debug = bool(getenv("DEBUG", "False") == "True")
    logging_level = int(getenv("LOGGING_LEVEL", logging.INFO))
    db_echo = bool(getenv("DB_ECHO", "False") == "True")

    events_per_page = 2

    db = DatabaseConfig()
    bot = BotConfig()
    redis = RedisConfig()


conf = Configuration()
