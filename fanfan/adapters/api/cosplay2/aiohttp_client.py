from json import JSONDecodeError
from typing import Any

from aiohttp import ClientError, ClientResponse
from dataclass_rest.exceptions import ClientLibraryError, MalformedResponse
from dataclass_rest.http.aiohttp import AiohttpClient, AiohttpMethod


class C2AiohttpMethod(AiohttpMethod):
    async def _response_body(self, response: ClientResponse) -> Any:
        try:
            # C2 returns text/html instead of json
            return await response.json(content_type="text/html")
        except ClientError as e:
            raise ClientLibraryError from e
        except JSONDecodeError as e:
            raise MalformedResponse from e


class C2AiohttpClient(AiohttpClient):
    method_class = C2AiohttpMethod
