from redis.asyncio import Redis

from fanfan.adapters.redis.config import RedisConfig


def create_redis(config: RedisConfig) -> Redis:
    return Redis.from_url(config.build_connection_str(), decode_responses=True)
