from collections.abc import AsyncIterable

from aiohttp import ClientSession
from dishka import Provider, Scope, provide

from fanfan.adapters.api.cosplay2.client import Cosplay2Client
from fanfan.adapters.api.cosplay2.config import Cosplay2Config
from fanfan.adapters.api.cosplay2.exceptions import NoCosplay2ConfigProvided
from fanfan.adapters.config.models import EnvConfig


class Cosplay2Provider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_cosplay2_config(self, config: EnvConfig) -> Cosplay2Config:
        if config.cosplay2 is None:
            raise NoCosplay2ConfigProvided
        return config.cosplay2

    @provide
    async def get_cosplay2_client(
        self, config: Cosplay2Config
    ) -> AsyncIterable[Cosplay2Client]:
        headers = {
            "X-API-Key": config.api_key,
            "X-API-Secret": config.api_secret.get_secret_value(),
        }
        async with ClientSession(headers=headers) as session:
            yield Cosplay2Client(base_url=config.build_api_base_url(), session=session)
