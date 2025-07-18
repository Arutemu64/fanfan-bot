from dishka import AsyncContainer, Provider, make_async_container
from dishka.integrations.aiogram import AiogramProvider
from dishka.integrations.fastapi import FastapiProvider

from fanfan.main.ioc.auth import (
    BotAuthProvider,
    JwtTokenProcessorProvider,
    SystemAuthProvider,
    WebAuthProvider,
)
from fanfan.main.ioc.bot import BotProvider, BotUtilsProvider
from fanfan.main.ioc.config import ConfigProvider
from fanfan.main.ioc.cosplay2 import Cosplay2Provider
from fanfan.main.ioc.db import DbProvider
from fanfan.main.ioc.dp import DpProvider, ExternalBgmFactoryProvider
from fanfan.main.ioc.interactors import InteractorsProvider
from fanfan.main.ioc.redis import RedisProvider
from fanfan.main.ioc.repositories import RepositoriesProvider
from fanfan.main.ioc.services import ServicesProvider
from fanfan.main.ioc.stream import StreamProvider
from fanfan.main.ioc.tcloud import TCloudProvider
from fanfan.main.ioc.utils import UtilsProvider


def get_common_providers() -> list[Provider]:
    return [
        ConfigProvider(),
        JwtTokenProcessorProvider(),
        DbProvider(),
        InteractorsProvider(),
        BotProvider(),
        BotUtilsProvider(),
        RedisProvider(),
        TCloudProvider(),
        ServicesProvider(),
        RepositoriesProvider(),
        UtilsProvider(),
        StreamProvider(),
        Cosplay2Provider(),
    ]


def create_bot_container() -> AsyncContainer:
    providers = get_common_providers()
    providers += [AiogramProvider(), BotAuthProvider(), DpProvider()]
    return make_async_container(*providers)


def create_web_container() -> AsyncContainer:
    providers = get_common_providers()
    providers += [FastapiProvider(), WebAuthProvider(), ExternalBgmFactoryProvider()]
    return make_async_container(*providers)


def create_system_container() -> AsyncContainer:
    providers = get_common_providers()
    providers += [SystemAuthProvider(), ExternalBgmFactoryProvider()]
    return make_async_container(*providers)
