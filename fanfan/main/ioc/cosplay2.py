from collections.abc import AsyncIterable
from typing import NewType

from aiohttp import ClientSession
from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from fanfan.adapters.api.cosplay2.client import Cosplay2Client
from fanfan.adapters.config.models import Cosplay2Config

Cosplay2Session = NewType("Cosplay2Session", ClientSession)


class Cosplay2Provider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_cosplay2_session(self) -> AsyncIterable[Cosplay2Session]:
        async with ClientSession() as session:
            yield session

    @provide
    async def get_cosplay2_client(
        self, session: Cosplay2Session, config: Cosplay2Config | None, redis: Redis
    ) -> Cosplay2Client | None:
        if config:
            return Cosplay2Client(session, config, redis)
        return None
