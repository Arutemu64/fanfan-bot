from dishka import Provider, Scope, provide

from fanfan.adapters.config.models import (
    EnvConfig,
)
from fanfan.adapters.config.parsers import get_config
from fanfan.adapters.debug.config import DebugConfig
from fanfan.presentation.web.config import WebConfig


class ConfigProvider(Provider):
    scope = Scope.APP

    @provide
    def get_config(self) -> EnvConfig:
        return get_config()

    @provide
    def get_web_config(self, config: EnvConfig) -> WebConfig:
        return config.web

    @provide
    def get_debug_config(self, config: EnvConfig) -> DebugConfig:
        return config.debug
