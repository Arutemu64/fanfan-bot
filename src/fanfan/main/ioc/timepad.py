from collections.abc import AsyncIterable
from typing import NewType

from aiohttp import ClientSession
from dishka import Provider, Scope, provide

from fanfan.adapters.api.timepad.client import TimepadClient
from fanfan.adapters.config.models import TimepadConfig

TimepadSession = NewType("TimepadSession", ClientSession)


class TimepadProvider(Provider):
    scope = Scope.REQUEST

    @provide
    async def get_timepad_session(self) -> AsyncIterable[TimepadSession]:
        async with ClientSession() as session:
            yield TimepadSession(session)

    @provide
    async def get_timepad_client(
        self, session: TimepadSession, config: TimepadConfig | None = None
    ) -> TimepadClient | None:
        if config:
            client = TimepadClient(session, config)
            await client.auth()
            return client
        return None
