from collections.abc import AsyncIterable
from typing import NewType

from aiohttp import ClientSession
from dishka import Provider, Scope, provide

from fanfan.adapters.api.ticketscloud.client import TCloudClient
from fanfan.adapters.api.ticketscloud.config import TCloudConfig
from fanfan.adapters.api.ticketscloud.importer import TCloudImporter
from fanfan.adapters.config.models import Configuration

TCloudSession = NewType("TCloudSession", ClientSession)


class TCloudProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_tcloud_config(self, config: Configuration) -> TCloudConfig | None:
        return config.tcloud

    @provide
    async def get_tcloud_session(self) -> AsyncIterable[TCloudSession]:
        async with ClientSession() as session:
            yield TCloudSession(session)

    @provide
    async def get_tcloud_client(
        self, session: TCloudSession, config: TCloudConfig | None = None
    ) -> TCloudClient | None:
        if config:
            return TCloudClient(session, config)
        return None

    importer = provide(TCloudImporter)
