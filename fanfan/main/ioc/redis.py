from collections.abc import AsyncIterable

from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage, DefaultKeyBuilder
from aiogram.fsm.storage.redis import RedisEventIsolation, RedisStorage
from dishka import AnyOf, Provider, Scope, provide
from redis.asyncio import Redis

from fanfan.adapters.config_reader import RedisConfig


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_redis(self, config: RedisConfig) -> AsyncIterable[Redis]:
        async with Redis.from_url(
            config.build_connection_str(), decode_responses=True
        ) as redis:
            yield redis

    @provide
    def create_redis_storage(
        self,
        redis: Redis,
        config: RedisConfig,
    ) -> AnyOf[RedisStorage, BaseStorage]:
        return RedisStorage(
            redis=redis,
            key_builder=DefaultKeyBuilder(with_destiny=True),
            state_ttl=config.state_ttl,
            data_ttl=config.data_ttl,
        )

    @provide
    def get_redis_event_isolation(
        self,
        storage: RedisStorage,
    ) -> AnyOf[RedisEventIsolation, BaseEventIsolation]:
        return storage.create_isolation()
