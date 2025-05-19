import logging

from adaptix import Retort
from aiohttp import ClientSession

from fanfan.adapters.api.timepad.dto.order import RegistrationOrdersResponse
from fanfan.adapters.config.models import TimepadConfig

logger = logging.getLogger(__name__)


class TimepadClient:
    def __init__(self, session: ClientSession, config: TimepadConfig) -> None:
        self.session = session
        self.base_url = "https://api.timepad.ru/"
        self.retort = Retort(strict_coercion=False)
        self.config = config

    async def auth(self):
        self.session.headers.update(
            {"Authorization": f"Bearer {self.config.client_id.get_secret_value()}"}
        )

    async def get_orders(
        self,
        event_id: int,
        limit: int = 10,
        skip: int = 0,
    ) -> RegistrationOrdersResponse:
        url = self.base_url + f"v1/events/{event_id}/orders"
        response = await self.session.get(url, params={"limit": limit, "skip": skip})
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
        return self.retort.load(data, RegistrationOrdersResponse)
