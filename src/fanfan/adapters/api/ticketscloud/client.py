import logging
from typing import TypeVar

from adaptix import Retort
from descanso import RestBuilder
from descanso.http.aiohttp import AiohttpClient

from fanfan.adapters.api.ticketscloud.dto.order import OrdersResponse
from fanfan.adapters.api.ticketscloud.dto.refund import RefundsResponse

OutputType = TypeVar("OutputType")

logger = logging.getLogger(__name__)

rest = RestBuilder(
    request_body_dumper=Retort(),
    response_body_loader=Retort(),
    query_param_dumper=Retort(),
)


class TCloudClient(AiohttpClient):
    @rest.get("resources/orders")
    async def get_orders(self, page: int = 1, page_size: int = 200) -> OrdersResponse:
        pass

    @rest.get("resources/refund_requests")
    async def get_refunds(self, page: int = 1, page_size: int = 200) -> RefundsResponse:
        pass
