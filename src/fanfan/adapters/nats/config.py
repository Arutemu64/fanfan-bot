from pydantic import BaseModel, NatsDsn, SecretStr


class NatsConfig(BaseModel):
    host: str
    port: int
    user: str
    password: SecretStr

    def build_connection_str(self) -> str:
        dsn: NatsDsn = NatsDsn.build(
            scheme="nats",
            host=self.host,
            port=self.port,
            username=self.user,
            password=self.password.get_secret_value(),
        )
        return dsn.unicode_string()
