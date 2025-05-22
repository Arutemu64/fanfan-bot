from pydantic import BaseModel, SecretStr


class Cosplay2Config(BaseModel):
    subdomain: str
    login: str
    password: SecretStr

    def build_api_base_url(self) -> str:
        return f"https://{self.subdomain}.cosplay2.ru/api/"
