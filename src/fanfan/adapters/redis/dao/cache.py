import json
from typing import Any, TypeVar

from redis.asyncio import Redis

from fanfan.adapters.redis.utils import RedisRetort

OutputType = TypeVar("OutputType")

DEFAULT_CACHE_TTL = 60


class CacheAdapter:
    def __init__(self, redis: Redis, retort: RedisRetort):
        self.redis = redis
        self.retort = retort

    @staticmethod
    def _build_cache_key(key: str) -> str:
        return f"cache:{key}"

    async def set_cache(
        self, key: str, data: Any, ttl: int = DEFAULT_CACHE_TTL
    ) -> None:
        cache_key = self._build_cache_key(key)

        dumped = self.retort.dump(data)
        serialized = dumped if isinstance(dumped, (str, bytes)) else json.dumps(dumped)

        await self.redis.set(
            name=cache_key,
            value=serialized,
            ex=ttl,
        )

    async def get_cache(
        self, key: str, output_type: type[OutputType]
    ) -> OutputType | None:
        cache_key = self._build_cache_key(key)
        data = await self.redis.get(name=cache_key)
        if data is None:
            return None

        if isinstance(data, bytes):
            data = data.decode()

        try:
            parsed = json.loads(data)
        except json.JSONDecodeError:
            parsed = data

        return self.retort.load(parsed, output_type)
