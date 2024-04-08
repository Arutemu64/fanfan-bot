from typing import List

from dishka import Provider

from fanfan.infrastructure.di.bot import BotProvider, DpProvider
from fanfan.infrastructure.di.config import ConfigProvider
from fanfan.infrastructure.di.db import DbProvider, RedisProvider
from fanfan.infrastructure.di.user_bot import UserProvider


def get_common_providers() -> List[Provider]:
    return [
        ConfigProvider(),
        DbProvider(),
    ]


def get_app_providers() -> List[Provider]:
    return [
        *get_common_providers(),
        DpProvider(),
        BotProvider(),
        RedisProvider(),
    ]


def get_bot_providers() -> List[Provider]:
    return [*get_common_providers(), UserProvider()]
