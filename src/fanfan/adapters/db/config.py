from pydantic import BaseModel, PostgresDsn, SecretStr


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
