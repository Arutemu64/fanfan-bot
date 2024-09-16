from collections.abc import AsyncIterable
from typing import NewType

from aiohttp import ClientSession
from dishka import Provider, Scope, provide

from fanfan.common.config import TimepadConfig
from fanfan.infrastructure.timepad.client import TimepadClient

TimepadSession = NewType("TimepadSession", ClientSession)


class TimepadProvider(Provider):
    scope = Scope.APP

    @provide(scope=Scope.REQUEST)
    async def get_timepad_session(
        self,
        config: TimepadConfig,
    ) -> AsyncIterable[TimepadSession]:
        async with ClientSession(
            headers={"Authorization": f"Bearer {config.client_id.get_secret_value()}"},
        ) as session:
            yield session

    @provide(scope=Scope.REQUEST)
    async def get_timepad_client(self, session: TimepadSession) -> TimepadClient:
        return TimepadClient(session)
