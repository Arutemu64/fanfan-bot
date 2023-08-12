from redis.asyncio.client import Redis


class VotingEnabled:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self) -> bool | None:
        voting_enabled = int(await self.redis.get("voting_enabled"))
        if voting_enabled == 1:
            return True
        elif voting_enabled == 0:
            return False
        else:
            return None

    async def set(self, value: bool):
        if value:
            await self.redis.set("voting_enabled", "1")
        else:
            await self.redis.set("voting_enabled", "0")


class AnnouncementTimestamp:
    def __init__(self, redis: Redis):
        self.redis = redis

    async def get(self) -> float | None:
        announcement_timestamp = await self.redis.get("announcement_timestamp")
        if announcement_timestamp:
            return float(announcement_timestamp)
        else:
            return None

    async def set(self, timestamp: float):
        await self.redis.set("announcement_timestamp", str(timestamp))


class Settings:
    voting_enabled: VotingEnabled
    announcement_timestamp: AnnouncementTimestamp

    def __init__(self, redis: Redis):
        self.redis = redis
        self.voting_enabled = VotingEnabled(self.redis)
        self.announcement_timestamp = AnnouncementTimestamp(self.redis)
