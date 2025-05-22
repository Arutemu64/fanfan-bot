from dishka import Provider, Scope, provide

from fanfan.adapters.config.models import (
    Configuration,
    LimitsConfig,
)
from fanfan.adapters.config.parsers import get_config
from fanfan.common.debug.config import DebugConfig
from fanfan.presentation.web.config import WebConfig


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def get_config(self) -> Configuration:
        return get_config()

    @provide
    def get_web_config(self, config: Configuration) -> WebConfig:
        return config.web

    @provide()
    def get_limits(self, config: Configuration) -> LimitsConfig:
        return config.limits

    @provide
    def get_debug_config(self, config: Configuration) -> DebugConfig:
        return config.debug
