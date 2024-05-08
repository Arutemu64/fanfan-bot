from typing import AsyncIterable

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from fanfan.config import RedisConfig


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_redis(self, config: RedisConfig) -> AsyncIterable[Redis]:
        async with Redis.from_url(config.build_connection_str()) as redis:
            yield redis
