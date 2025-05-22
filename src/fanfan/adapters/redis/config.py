from pydantic import BaseModel, RedisDsn, SecretStr


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
