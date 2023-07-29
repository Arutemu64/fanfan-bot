from environs import Env
from sqlalchemy import URL

env = Env()
env.read_env(override=True)


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
