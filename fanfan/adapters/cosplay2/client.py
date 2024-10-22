import logging
from typing import Any

from adaptix import Retort
from aiohttp import ClientSession
from dataclass_rest import get
from dataclass_rest.http_request import HttpRequest
from redis.asyncio import Redis

from fanfan.adapters.config_reader import Cosplay2Config
from fanfan.adapters.cosplay2.aiohttp_client import (
    C2AiohttpClient,
)
from fanfan.adapters.cosplay2.dto.requests import Request
from fanfan.adapters.cosplay2.dto.topics import Topic

logger = logging.getLogger(__name__)

COSPLAY2_AUTH_SSID_KEY = "cosplay2:auth_ssid"


class Cosplay2Client(C2AiohttpClient):
    def __init__(self, session: ClientSession, config: Cosplay2Config, redis: Redis):
        self.config = config
        self.redis = redis
        super().__init__(
            base_url=config.build_api_base_url(),
            session=session,
        )

    async def do_request(self, request: HttpRequest) -> Any:
        # Get cached auth_ssid from Redis
        auth_ssid = await self.redis.get(COSPLAY2_AUTH_SSID_KEY)
        # Check if it fails
        if auth_ssid:
            test = await self.session.get(
                url=f"{self.base_url}events/get_settings",
                cookies={"auth_ssid": auth_ssid},
            )
            if test.ok:
                logger.info("Using cached auth_ssid")
            else:
                logger.info("auth_ssid has expired, will be renewed")
                auth_ssid = None
        if auth_ssid is None:
            # Login into C2 and grab fresh auth_ssid
            login_response = await self.session.post(
                url=f"{self.base_url}users/login",
                data={
                    "name": self.config.login,
                    "password": self.config.password.get_secret_value(),
                },
            )
            auth_ssid = login_response.cookies.get("auth_ssid").value
            logger.info("auth_ssid was renewed")
        # Update cookie jar
        self.session.cookie_jar.update_cookies(cookies={"auth_ssid": auth_ssid})
        # And don't forget to update cached auth_ssid
        await self.redis.set(COSPLAY2_AUTH_SSID_KEY, auth_ssid)
        # Now let's make a request!
        return await super().do_request(request)

    def _init_response_body_factory(self) -> Retort:
        return Retort(strict_coercion=False)

    @get("topics/get_all_requests")
    async def get_all_requests(self) -> list[Request]:
        pass

    @get("topics/get_list")
    async def get_topics_list(self) -> list[Topic]:
        pass
