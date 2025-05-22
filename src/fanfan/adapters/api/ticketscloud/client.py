import logging
from typing import TypeVar

from adaptix import Retort
from aiohttp import ClientSession

from fanfan.adapters.api.ticketscloud.config import TCloudConfig
from fanfan.adapters.api.ticketscloud.dto.order import OrdersResponse
from fanfan.adapters.api.ticketscloud.dto.refund import RefundsResponse

OutputType = TypeVar("OutputType")

logger = logging.getLogger(__name__)


class TCloudClient:
    def __init__(self, session: ClientSession, config: TCloudConfig) -> None:
        self.session = session
        self.base_url = "https://ticketscloud.com/v2/"
        self.retort = Retort(strict_coercion=False)
        self.config = config
        self.session.headers.update(
            {"Authorization": f"key {self.config.api_key.get_secret_value()}"}
        )

    async def _do_request(
        self, path: str, params: dict, output_type: type[OutputType]
    ) -> OutputType:
        url = self.base_url + path
        response = await self.session.get(url, params=params)
        if response.status != 200:
            error_text = await response.text()
            logger.error(
                "Request to % failed with status %s: %s",
                url,
                response.status,
                error_text,
            )
            response.raise_for_status()
        data = await response.json()
        return self.retort.load(data, output_type)

    async def get_orders(self, page: int = 1, page_size: int = 200) -> OrdersResponse:
        return await self._do_request(
            path="resources/orders",
            params={"page": page, "page_size": page_size},
            output_type=OrdersResponse,
        )

    async def get_refunds(self, page: int = 1, page_size: int = 200) -> RefundsResponse:
        return await self._do_request(
            path="resources/refund_requests",
            params={"page": page, "page_size": page_size},
            output_type=RefundsResponse,
        )
