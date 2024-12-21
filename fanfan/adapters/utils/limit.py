import datetime

from redis.asyncio import Redis
from redis.asyncio.lock import Lock

from fanfan.core.exceptions.limiter import LimitLocked, TooFast


class Limit:
    def __init__(
        self, redis: Redis, lock: Lock, timestamp_key: str, cooldown_period: float
    ):
        self.redis = redis
        self.lock = lock
        self.timestamp_key = timestamp_key
        self.cooldown_period = cooldown_period

    async def _get_redis_time(self) -> float:
        return float((await self.redis.time())[0])

    async def _get_last_timestamp(self) -> float | None:
        last_timestamp = await self.redis.get(self.timestamp_key)
        if last_timestamp:
            return float(last_timestamp)
        return None

    async def __aenter__(self) -> None:
        if await self.lock.acquire() is False:
            raise LimitLocked
        last_timestamp = await self._get_last_timestamp() or 0
        if (await self._get_redis_time() - last_timestamp) < self.cooldown_period:
            await self.lock.release()
            raise TooFast(
                cooldown_period=self.cooldown_period, timestamp=last_timestamp
            )

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            await self.redis.set(self.timestamp_key, await self._get_redis_time())
        await self.lock.release()

    async def locked(self) -> bool:
        return await self.lock.locked()

    async def get_last_execution(self) -> datetime.datetime | None:
        timestamp = await self._get_last_timestamp()
        if timestamp:
            return datetime.datetime.fromtimestamp(timestamp, datetime.UTC)
        return None


class LimitFactory:
    def __init__(self, redis: Redis):
        self.redis = redis

    def __call__(
        self,
        limit_name: str,
        cooldown_period: float = 60,
        blocking: bool = True,
        lock_timeout: float = 60,
    ) -> Limit:
        return Limit(
            redis=self.redis,
            lock=self.redis.lock(
                name=f"limiter:{limit_name}:lock",
                timeout=lock_timeout,
                blocking=blocking,
            ),
            timestamp_key=f"limiter:{limit_name}:timestamp",
            cooldown_period=cooldown_period,
        )
