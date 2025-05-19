from dishka import Provider, Scope, provide

from fanfan.adapters.auth.providers.system import SystemIdProvider
from fanfan.adapters.auth.providers.telegram import TelegramIdProvider
from fanfan.adapters.auth.providers.web import WebIdProvider
from fanfan.adapters.auth.utils.token import JwtTokenProcessor
from fanfan.application.common.id_provider import IdProvider


class JwtTokenProcessorProvider(Provider):
    token_processor = provide(JwtTokenProcessor, scope=Scope.APP)


class TelegramAuthProvider(Provider):
    scope = Scope.REQUEST

    telegram_id_provider = provide(TelegramIdProvider, provides=IdProvider)


class WebAuthProvider(Provider):
    scope = Scope.REQUEST

    web_id_provider = provide(WebIdProvider, provides=IdProvider)


class SystemAuthProvider(Provider):
    scope = Scope.REQUEST

    system_id_provider = provide(SystemIdProvider, provides=IdProvider)
