from dishka import Provider, Scope, provide

from fanfan.adapters.config.models import (
    BotConfig,
    Configuration,
    Cosplay2Config,
    DatabaseConfig,
    DebugConfig,
    LimitsConfig,
    NatsConfig,
    RedisConfig,
    TimepadConfig,
    WebConfig,
)
from fanfan.adapters.config.parsers import get_config


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def get_config(self) -> Configuration:
        return get_config()

    @provide
    def get_bot_config(self, config: Configuration) -> BotConfig:
        return config.bot

    @provide
    def get_web_config(self, config: Configuration) -> WebConfig:
        return config.web

    @provide
    def get_db_config(self, config: Configuration) -> DatabaseConfig:
        return config.db

    @provide
    def get_redis_config(self, config: Configuration) -> RedisConfig:
        return config.redis

    @provide()
    def get_nats_config(self, config: Configuration) -> NatsConfig:
        return config.nats

    @provide()
    def get_limits(self, config: Configuration) -> LimitsConfig:
        return config.limits

    @provide
    def get_debug_config(self, config: Configuration) -> DebugConfig:
        return config.debug

    @provide
    def get_timepad_config(self, config: Configuration) -> TimepadConfig | None:
        return config.timepad

    @provide()
    def get_cosplay2_config(self, config: Configuration) -> Cosplay2Config | None:
        return config.cosplay2
