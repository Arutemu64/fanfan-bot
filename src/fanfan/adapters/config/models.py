from pydantic import (
    BaseModel,
    DirectoryPath,
    HttpUrl,
)
from pydantic_extra_types.timezone_name import TimeZoneName
from pydantic_settings import BaseSettings, SettingsConfigDict

from fanfan.adapters.api.cosplay2.config import Cosplay2Config
from fanfan.adapters.api.ticketscloud.config import TCloudConfig
from fanfan.adapters.db.config import DatabaseConfig
from fanfan.adapters.debug.config import DebugConfig
from fanfan.adapters.nats.config import NatsConfig
from fanfan.adapters.redis.config import RedisConfig
from fanfan.presentation.tgbot.config import BotConfig
from fanfan.presentation.web.config import WebConfig


class LimitsConfig(BaseModel):
    announcement_timeout: int = 10


class Configuration(BaseSettings):
    model_config = SettingsConfigDict(env_nested_delimiter="__")

    env: str
    timezone: TimeZoneName = "Europe/Moscow"
    media_root: DirectoryPath
    docs_link: HttpUrl | None = None

    bot: BotConfig
    web: WebConfig

    db: DatabaseConfig
    redis: RedisConfig
    nats: NatsConfig

    limits: LimitsConfig
    debug: DebugConfig

    cosplay2: Cosplay2Config | None = None
    tcloud: TCloudConfig | None = None
