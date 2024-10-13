from aiogram.types import (
    TelegramObject,
)
from dishka import Provider, Scope, from_context, provide
from fastapi import Request

from fanfan.application.common.id_provider import IdProvider
from fanfan.infrastructure.auth.providers.stub import StubIdProvider
from fanfan.infrastructure.auth.providers.telegram import TelegramIdProvider
from fanfan.infrastructure.auth.providers.web import WebIdProvider
from fanfan.infrastructure.auth.utils.token import JwtTokenProcessor


class JwtTokenProcessorProvider(Provider):
    token_processor = provide(JwtTokenProcessor, scope=Scope.APP)


class TelegramAuthProvider(Provider):
    scope = Scope.REQUEST
    obj = from_context(
        provides=TelegramObject,
        scope=Scope.REQUEST,
    )

    telegram_id_provider = provide(TelegramIdProvider, provides=IdProvider)


class WebAuthProvider(Provider):
    scope = Scope.REQUEST
    request = from_context(Request, scope=Scope.REQUEST)

    web_id_provider = provide(WebIdProvider, provides=IdProvider)


class StubAuthProvider(Provider):
    scope = Scope.REQUEST

    stub_id_provider = provide(StubIdProvider, provides=IdProvider)
