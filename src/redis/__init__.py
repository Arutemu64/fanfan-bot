import pickle

from aiogram.fsm.storage.redis import DefaultKeyBuilder, RedisStorage
from redis.asyncio import Redis

from src.config import conf


def build_redis_client() -> Redis:
    """Build redis client"""
    client = Redis(
        host=conf.redis.host,
        db=conf.redis.db,
        port=conf.redis.port,
        password=conf.redis.passwd,
        username=conf.redis.username,
    )
    return client


def get_redis_storage(
    redis: Redis, state_ttl=conf.redis.state_ttl, data_ttl=conf.redis.data_ttl
) -> RedisStorage:
    return RedisStorage(
        redis=redis,
        state_ttl=state_ttl,
        data_ttl=data_ttl,
        key_builder=DefaultKeyBuilder(with_destiny=True),
    )


class RedisNativeClient:
    def __init__(self, client: Redis, key: str):
        self.client = client
        self.key = key

    async def exists(self):
        return await self.client.exists(self.key)

    async def set(self, value):
        return await self.client.set(self.key, pickle.dumps(value))

    async def get(self):
        value = await self.client.get(self.key)
        if value:
            return pickle.loads(value)
        return None

    async def create(self, value):
        if not await self.client.exists(self.key):
            return await self.set(value)
