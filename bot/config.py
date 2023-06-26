from os import getenv
import os
from sqlalchemy.engine import URL
from dataclasses import dataclass
import logging


class DatabaseConfig:
    """Database connection variables"""

    name: str = getenv("POSTGRES_DATABASE")
    user: str = getenv("POSTGRES_USER", "docker")
    passwd: str = getenv("POSTGRES_PASSWORD", None)
    port: int = int(getenv("POSTGRES_PORT", 5432))
    host: str = getenv("POSTGRES_HOST", "db")

    driver: str = "psycopg"
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


@dataclass
class BotConfig:
    """Bot configuration"""

    token: str = getenv("BOT_TOKEN")
    mode: str = getenv("MODE", 'polling')

    ngrok_auth: str = getenv("NGROK_AUTH")


@dataclass
class Configuration:
    """All in one configuration's class"""

    # debug = bool(getenv("DEBUG"))
    logging_level = int(getenv("LOGGING_LEVEL", logging.INFO))
    db_echo = bool(getenv("DB_ECHO", "False") == "True")
    ngrok_region = getenv("NGROK_REGION", "eu")

    channel_id = int(getenv("CHANNEL_ID"))
    channel_link = getenv("CHANNEL_LINK")

    db = DatabaseConfig()
    bot = BotConfig()


conf = Configuration()
