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
