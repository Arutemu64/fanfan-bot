import datetime
import time
from datetime import timedelta

from redis.asyncio import Redis
from redis.asyncio.lock import Lock

from fanfan.core.exceptions.limiter import LimitLocked, TooFast


class Limit:
    def __init__(
        self, lock: Lock, redis: Redis, timestamp_key: str, limit_timeout: float
    ):
        self.lock = lock
        self.redis = redis
        self.timestamp_key = timestamp_key
        self.limit_timeout = limit_timeout

    async def _get_timestamp(self) -> float | None:
        timestamp = await self.redis.get(self.timestamp_key)
        if timestamp:
            return float(timestamp)
        return None

    async def __aenter__(self) -> None:
        if await self.lock.acquire() is False:
            raise LimitLocked
        current_timestamp = await self._get_timestamp() or 0
        if (time.time() - current_timestamp) < self.limit_timeout:
            await self.lock.release()
            raise TooFast(
                limit_timeout=self.limit_timeout, current_timestamp=current_timestamp
            )

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            await self.redis.set(self.timestamp_key, time.time())
        await self.lock.release()

    async def locked(self) -> bool:
        return await self.lock.locked()

    async def get_last_execution(self) -> datetime.datetime | None:
        timestamp = await self._get_timestamp()
        if timestamp:
            return datetime.datetime.fromtimestamp(timestamp, datetime.UTC)
        return None


class LimitFactory:
    def __init__(self, redis: Redis):
        self.redis = redis

    def __call__(
        self,
        limit_name: str,
        limit_timeout: float = timedelta(minutes=1).seconds,
        blocking: bool = True,
        lock_timeout: float = timedelta(minutes=1).seconds,
    ) -> Limit:
        return Limit(
            lock=self.redis.lock(
                name=f"limiter:{limit_name}:lock",
                timeout=lock_timeout,
                blocking=blocking,
            ),
            redis=self.redis,
            timestamp_key=f"limiter:{limit_name}:timestamp",
            limit_timeout=limit_timeout,
        )
