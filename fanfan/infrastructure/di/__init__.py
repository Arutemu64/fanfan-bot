from typing import List

from dishka import Provider


def get_app_providers() -> List[Provider]:
    from fanfan.infrastructure.di.bot import BotProvider, DpProvider
    from fanfan.infrastructure.di.config import ConfigProvider
    from fanfan.infrastructure.di.db import DbProvider
    from fanfan.infrastructure.di.redis import RedisProvider
    from fanfan.infrastructure.di.timepad import TimepadProvider

    return [
        ConfigProvider(),
        DbProvider(),
        DpProvider(),
        BotProvider(),
        RedisProvider(),
        TimepadProvider(),
    ]


def get_bot_providers() -> List[Provider]:
    from fanfan.infrastructure.di.user_bot import UserProvider

    return [*get_app_providers(), UserProvider()]
