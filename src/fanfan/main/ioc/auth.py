from dishka import Provider, Scope, provide

from fanfan.adapters.auth.providers.bot import BotIdProvider
from fanfan.adapters.auth.providers.system import SystemIdProvider
from fanfan.adapters.auth.providers.web import WebIdProvider
from fanfan.adapters.auth.utils.token import JwtTokenProcessor
from fanfan.application.common.id_provider import IdProvider


class JwtTokenProcessorProvider(Provider):
    token_processor = provide(JwtTokenProcessor, scope=Scope.APP)


class BotAuthProvider(Provider):
    scope = Scope.REQUEST

    bot_id_provider = provide(BotIdProvider, provides=IdProvider)


class WebAuthProvider(Provider):
    scope = Scope.REQUEST

    web_id_provider = provide(WebIdProvider, provides=IdProvider)


class SystemAuthProvider(Provider):
    scope = Scope.REQUEST

    system_id_provider = provide(SystemIdProvider, provides=IdProvider)
