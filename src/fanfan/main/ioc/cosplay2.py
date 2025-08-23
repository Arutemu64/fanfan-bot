from collections.abc import AsyncIterable
from typing import NewType

from aiohttp import ClientSession
from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from fanfan.adapters.api.cosplay2.client import Cosplay2Client
from fanfan.adapters.api.cosplay2.config import Cosplay2Config
from fanfan.adapters.api.cosplay2.exceptions import NoCosplay2ConfigProvided
from fanfan.adapters.api.cosplay2.importer import Cosplay2Importer
from fanfan.adapters.config.models import EnvConfig

Cosplay2Session = NewType("Cosplay2Session", ClientSession)


class Cosplay2Provider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_cosplay2_config(self, config: EnvConfig) -> Cosplay2Config:
        if config.cosplay2 is None:
            raise NoCosplay2ConfigProvided
        return config.cosplay2

    @provide
    async def get_cosplay2_session(self) -> AsyncIterable[Cosplay2Session]:
        async with ClientSession() as session:
            yield Cosplay2Session(session)

    @provide
    async def get_cosplay2_client(
        self, session: Cosplay2Session, config: Cosplay2Config, redis: Redis
    ) -> Cosplay2Client:
        client = Cosplay2Client(session, config, redis)
        await client.auth()
        return client

    importer = provide(Cosplay2Importer)
