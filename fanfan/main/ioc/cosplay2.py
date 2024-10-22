from collections.abc import AsyncIterable
from typing import NewType

from aiohttp import ClientSession
from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from fanfan.adapters.config_reader import Cosplay2Config
from fanfan.adapters.cosplay2.client import Cosplay2Client

Cosplay2Session = NewType("Cosplay2Session", ClientSession)


class Cosplay2Provider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_cosplay2_session(self) -> AsyncIterable[Cosplay2Session]:
        async with ClientSession() as session:
            yield session

    @provide
    async def get_cosplay2_client(
        self, session: Cosplay2Session, config: Cosplay2Config, redis: Redis
    ) -> Cosplay2Client:
        return Cosplay2Client(session, config, redis)
