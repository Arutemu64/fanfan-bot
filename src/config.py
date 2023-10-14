import logging
from dataclasses import dataclass

from environs import Env
from sqlalchemy.engine import URL

env = Env()
env.read_env()


class DatabaseConfig:
    """Database connection variables"""

    name: str = env("POSTGRES_DATABASE")
    user: str = env("POSTGRES_USER", "docker")
    passwd: str = env("POSTGRES_PASSWORD", None)
    port: int = env.int("POSTGRES_PORT", 5432)
    host: str = env("POSTGRES_HOST", "db")

    # driver: str = "asyncpg"
    database_system: str = "postgresql"

    def build_connection_str(self, driver: str = "asyncpg") -> str:
        """
        This function build a connection string
        """
        return URL.create(
            drivername=f"{self.database_system}+{driver}",
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
    secret_key: str = env("SECRET_KEY")
    mode: str = env("MODE", "polling")
    if mode == "webhook":
        webhook_domain: str = env("WEBHOOK_DOMAIN")
        webhook_path: str = env("WEBHOOK_PATH")
        web_server_host: str = env("WEB_SERVER_HOST")
        web_server_port: int = env.int("WEB_SERVER_PORT")

    web_panel_link: str = env("WEB_PANEL_LINK")

    admin_list = env.list("ADMIN_LIST", [])
    admin_list = [x.lower() for x in admin_list]

    sentry_logging_enabled: bool = env.bool("SENTRY_LOGGING_ENABLED", False)
    if sentry_logging_enabled:
        sentry_dsn: str = env("SENTRY_DSN")
        sentry_env: str = env("SENTRY_ENV")

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
