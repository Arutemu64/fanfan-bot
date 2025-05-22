from collections.abc import AsyncIterable

from aiogram.fsm.storage.base import BaseEventIsolation, BaseStorage
from aiogram.fsm.storage.redis import RedisEventIsolation, RedisStorage
from dishka import AnyOf, Provider, Scope, provide
from redis.asyncio import Redis

from fanfan.adapters.config.models import Configuration
from fanfan.adapters.redis.config import RedisConfig
from fanfan.adapters.redis.dao.cache import CacheAdapter
from fanfan.adapters.redis.factory import create_redis
from fanfan.adapters.redis.utils import RedisRetort, get_redis_retort
from fanfan.presentation.tgbot.factory import (
    create_redis_isolation,
    create_redis_storage,
)


class RedisProvider(Provider):
    scope = Scope.APP

    @provide
    def get_redis_config(self, config: Configuration) -> RedisConfig:
        return config.redis

    @provide
    async def get_redis(self, config: RedisConfig) -> AsyncIterable[Redis]:
        async with create_redis(config) as redis:
            yield redis

    @provide
    def get_redis_storage(
        self,
        redis: Redis,
        config: RedisConfig,
    ) -> AnyOf[RedisStorage, BaseStorage]:
        return create_redis_storage(redis, config)

    @provide
    def get_redis_event_isolation(
        self,
        storage: RedisStorage,
    ) -> AnyOf[RedisEventIsolation, BaseEventIsolation]:
        return create_redis_isolation(storage)

    @provide
    def get_redis_retort(self) -> RedisRetort:
        return get_redis_retort()

    cache_adapter = provide(CacheAdapter)
