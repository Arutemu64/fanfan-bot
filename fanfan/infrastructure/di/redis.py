from typing import AsyncIterable, NewType

from dishka import Provider, Scope, provide
from redis.asyncio import Redis

from fanfan.config import RedisConfig

SchedulerRedis = NewType("SchedulerRedis", Redis)


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_redis(self, config: RedisConfig) -> AsyncIterable[Redis]:
        async with Redis.from_url(config.build_connection_str()) as redis:
            yield redis

    @provide
    async def get_scheduler_redis(
        self, config: RedisConfig
    ) -> AsyncIterable[SchedulerRedis]:
        async with Redis.from_url(config.build_connection_str(database="1")) as redis:
            yield redis
