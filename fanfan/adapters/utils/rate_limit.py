import datetime

from redis.asyncio import Redis
from redis.asyncio.lock import Lock

from fanfan.core.exceptions.limiter import RateLimitCooldown, RateLimiterInUse


class RateLimit:
    def __init__(
        self, redis: Redis, lock: Lock, timestamp_key: str, cooldown_period: float
    ):
        self.redis = redis
        self.lock = lock
        self.timestamp_key = timestamp_key
        self.cooldown_period = cooldown_period

    async def _get_redis_time(self) -> float:
        seconds, microseconds = await self.redis.time()
        return seconds + microseconds / 1_000_000

    async def _get_last_timestamp(self) -> float | None:
        value = await self.redis.get(self.timestamp_key)
        return float(value) if value else None

    async def __aenter__(self) -> None:
        if not await self.lock.acquire():
            raise RateLimiterInUse

        now = await self._get_redis_time()
        last = await self._get_last_timestamp() or 0

        if (now - last) < self.cooldown_period:
            await self.lock.release()
            raise RateLimitCooldown(
                cooldown_period=self.cooldown_period, timestamp=last
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


class RateLimitFactory:
    def __init__(self, redis: Redis):
        self.redis = redis

    def __call__(
        self,
        limit_name: str,
        cooldown_period: float = 60,
        blocking: bool = True,
        lock_timeout: float = 60,
    ) -> RateLimit:
        return RateLimit(
            redis=self.redis,
            lock=self.redis.lock(
                name=f"rate_limit:{limit_name}:lock",
                timeout=lock_timeout,
                blocking=blocking,
            ),
            timestamp_key=f"rate_limit:{limit_name}:timestamp",
            cooldown_period=cooldown_period,
        )
