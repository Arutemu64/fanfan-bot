from pydantic import BaseModel, HttpUrl, SecretStr


class WebConfig(BaseModel):
    host: str
    port: int

    base_url: HttpUrl
    path: str = "/web"
    secret_key: SecretStr

    def build_admin_auth_url(self, token: str) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme=self.base_url.scheme,
            host=self.base_url.host,
            path=f"{self.path.lstrip('/')}/admin/auth?token={token}",
        )
        return url.unicode_string()

    def build_qr_scanner_url(self) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme=self.base_url.scheme,
            host=self.base_url.host,
            path=f"{self.path.lstrip('/')}/qr_scanner",
        )
        return url.unicode_string()
