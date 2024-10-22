from aiohttp import ClientSession
from dataclass_rest import get
from dataclass_rest.http.aiohttp import AiohttpClient

from fanfan.adapters.timepad.schemas import RegistrationOrdersResponse

TIMEPAD_API_BASE_URL = "https://api.timepad.ru/"


class TimepadClient(AiohttpClient):
    def __init__(self, session: ClientSession) -> None:
        super().__init__(base_url=TIMEPAD_API_BASE_URL, session=session)

    @get("v1/events/{event_id}/orders")
    async def get_orders(
        self,
        event_id: int,
        limit: int = 10,
        skip: int = 0,
    ) -> RegistrationOrdersResponse:
        pass
