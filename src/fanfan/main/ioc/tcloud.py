from collections.abc import AsyncIterable

from aiohttp import ClientSession
from dishka import Provider, Scope, provide

from fanfan.adapters.api.ticketscloud.client import TCloudClient
from fanfan.adapters.api.ticketscloud.config import TCloudConfig
from fanfan.adapters.api.ticketscloud.exceptions import NoTCloudConfigProvided
from fanfan.adapters.api.ticketscloud.importer import TCloudImporter
from fanfan.adapters.config.models import EnvConfig


class TCloudProvider(Provider):
    scope = Scope.REQUEST

    @provide(scope=Scope.APP)
    def get_tcloud_config(self, config: EnvConfig) -> TCloudConfig:
        if config.tcloud is None:
            raise NoTCloudConfigProvided
        return config.tcloud

    @provide
    async def get_tcloud_client(
        self, config: TCloudConfig
    ) -> AsyncIterable[TCloudClient]:
        headers = {"Authorization": f"key {config.api_key.get_secret_value()}"}
        async with ClientSession(headers=headers) as session:
            yield TCloudClient(base_url="https://ticketscloud.com/v2/", session=session)

    importer = provide(TCloudImporter)
