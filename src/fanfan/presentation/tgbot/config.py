import enum
from typing import Self

from pydantic import BaseModel, HttpUrl, SecretStr, model_validator


class BotMode(enum.StrEnum):
    POLLING = "polling"
    WEBHOOK = "webhook"


class WebhookConfig(BaseModel):
    host: str
    port: int

    base_url: HttpUrl
    path: str = "/webhook"

    def build_webhook_url(self) -> str:
        url: HttpUrl = HttpUrl.build(
            scheme=self.base_url.scheme,
            host=self.base_url.host,
            path=self.path.lstrip("/"),
        )
        return url.unicode_string()


class BotConfig(BaseModel):
    token: SecretStr
    mode: BotMode = BotMode.POLLING

    webhook: WebhookConfig | None = None

    @model_validator(mode="after")
    def check_if_webhook_config_set(self) -> Self:
        if self.mode is BotMode.WEBHOOK and self.webhook is None:
            msg = "Webhook config is not set!"
            raise AssertionError(msg)
        return self
