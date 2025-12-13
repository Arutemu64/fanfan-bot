from pydantic import BaseModel, SecretStr


class Cosplay2Config(BaseModel):
    event_id: int
    subdomain: str
    api_key: str
    api_secret: SecretStr

    def build_api_base_url(self) -> str:
        return f"https://{self.subdomain}.cosplay2.ru/api/"
