import logging

from adaptix import Retort
from descanso import RestBuilder
from descanso.http.aiohttp import AiohttpClient

from fanfan.adapters.api.cosplay2.dto.requests import Request, RequestValueDTO
from fanfan.adapters.api.cosplay2.dto.topics import Topic

logger = logging.getLogger(__name__)

rest = RestBuilder(
    request_body_dumper=Retort(),
    response_body_loader=Retort(),
    query_param_dumper=Retort(),
)


class Cosplay2Client(AiohttpClient):
    @rest.get("topics/get_all_requests")
    async def get_all_requests(self) -> list[Request]:
        pass

    @rest.get("topics/get_list")
    async def get_topics_list(self) -> list[Topic]:
        pass

    @rest.get("requests/get_all_values")
    async def get_all_values(self) -> list[RequestValueDTO]:
        pass
