from dishka import Provider, Scope, provide

from fanfan.adapters.config_reader import (
    BotConfig,
    Configuration,
    Cosplay2Config,
    DatabaseConfig,
    DebugConfig,
    NatsConfig,
    RedisConfig,
    TimepadConfig,
    WebConfig,
)


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def get_db_config(self) -> DatabaseConfig:
        return DatabaseConfig()

    @provide
    def get_redis_config(self) -> RedisConfig:
        return RedisConfig()

    @provide()
    def get_nats_config(self) -> NatsConfig:
        return NatsConfig()

    @provide
    def get_bot_config(self) -> BotConfig:
        return BotConfig()

    @provide
    def get_web_config(self) -> WebConfig:
        return WebConfig()

    @provide
    def get_timepad_config(self) -> TimepadConfig:
        return TimepadConfig()

    @provide()
    def get_cosplay2_config(self) -> Cosplay2Config:
        return Cosplay2Config()

    @provide
    def get_debug_config(self) -> DebugConfig:
        return DebugConfig()

    @provide
    def get_config(self) -> Configuration:
        return Configuration()
