import json
import logging
from typing import TypeVar

from adaptix import Retort
from aiohttp import ClientResponseError, ClientSession, ContentTypeError
from redis.asyncio import Redis

from fanfan.adapters.api.cosplay2.config import Cosplay2Config
from fanfan.adapters.api.cosplay2.dto.requests import Request
from fanfan.adapters.api.cosplay2.dto.topics import Topic

logger = logging.getLogger(__name__)

OutputType = TypeVar("OutputType")


class Cosplay2Client:
    _COSPLAY2_AUTH_COOKIES_KEY = "cosplay2:cookies"

    def __init__(self, session: ClientSession, config: Cosplay2Config, redis: Redis):
        self.session = session
        self.config = config
        self.redis = redis
        self.retort = Retort(strict_coercion=False)
        self.base_url = config.build_api_base_url()

    async def auth(self) -> None:
        # Try to load cached cookies from Redis
        if cached_cookies := await self.redis.get(self._COSPLAY2_AUTH_COOKIES_KEY):
            cookies = json.loads(cached_cookies)
            self.session.cookie_jar.update_cookies(cookies)

            # Check if cookies are still valid
            test_response = await self.session.get(
                f"{self.base_url}events/get_settings"
            )
            if test_response.ok:
                logger.info("Using cached cookies")
                return
            logger.info("Cached cookies are invalid, will re-authenticate")
            await self.redis.delete(self._COSPLAY2_AUTH_COOKIES_KEY)

        # If no valid cookies, log in and store fresh cookies
        login_response = await self.session.post(
            url=f"{self.base_url}users/login",
            data={
                "name": self.config.login,
                "password": self.config.password.get_secret_value(),
            },
        )

        if login_response.status != 200:
            login_response.raise_for_status()

        # Update cookies from the login response
        cookies = {key: morsel.value for key, morsel in login_response.cookies.items()}
        self.session.cookie_jar.update_cookies(cookies)
        await self.redis.set(self._COSPLAY2_AUTH_COOKIES_KEY, json.dumps(cookies))
        logger.info("Cookies were renewed and cached")

    async def _do_request(self, path: str, output_type: type[OutputType]) -> OutputType:
        url = self.base_url + path
        try:
            response = await self.session.get(url=url)

            if response.status != 200:
                error_text = await response.text()
                logger.error(
                    "Request to % failed with status %s: %s",
                    url,
                    response.status,
                    error_text,
                )
                response.raise_for_status()

            try:
                data = await response.json(
                    content_type="text/html"
                )  # This can raise ContentTypeError
            except ContentTypeError as e:
                text = await response.text()
                logger.exception(
                    "Failed to parse JSON from %s, got text instead: %s", url, text
                )
                msg = "Invalid JSON response"
                raise ValueError(msg) from e

            return self.retort.load(data, output_type)

        except ClientResponseError:
            logger.exception("HTTP error while requesting %s", url)
            raise
        except Exception:
            logger.exception("Unexpected error during request to %s", url)
            raise

    async def get_all_requests(self) -> list[Request]:
        return await self._do_request("topics/get_all_requests", list[Request])

    async def get_topics_list(self) -> list[Topic]:
        return await self._do_request("topics/get_list", list[Topic])
