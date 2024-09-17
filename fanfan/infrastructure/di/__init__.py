from dishka import AsyncContainer, Provider, make_async_container

from fanfan.infrastructure.di.auth import (
    JwtTokenProcessorProvider,
    StubAuthProvider,
    TelegramAuthProvider,
    WebAuthProvider,
)
from fanfan.infrastructure.di.bot import BotProvider, DpProvider, NotifierProvider
from fanfan.infrastructure.di.config import ConfigProvider
from fanfan.infrastructure.di.db import DbProvider
from fanfan.infrastructure.di.interactors import InteractorsProvider
from fanfan.infrastructure.di.jinja import JinjaProvider
from fanfan.infrastructure.di.redis import RedisProvider
from fanfan.infrastructure.di.timepad import TimepadProvider


def get_common_providers() -> list[Provider]:
    return [
        ConfigProvider(),
        JwtTokenProcessorProvider(),
        DbProvider(),
        InteractorsProvider(),
        NotifierProvider(),
        BotProvider(),
        DpProvider(),
        RedisProvider(),
        TimepadProvider(),
        JinjaProvider(),
    ]


def create_bot_container() -> AsyncContainer:
    providers = get_common_providers()
    providers += [TelegramAuthProvider()]
    return make_async_container(*providers)


def create_web_container() -> AsyncContainer:
    providers = get_common_providers()
    providers += [WebAuthProvider()]
    return make_async_container(*providers)


def create_scheduler_container() -> AsyncContainer:
    providers = get_common_providers()
    providers += [StubAuthProvider()]
    return make_async_container(*providers)
