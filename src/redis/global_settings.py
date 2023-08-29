from redis.asyncio import Redis

from src.redis import RedisNativeClient


class GlobalSettings:
    voting_enabled: RedisNativeClient
    announcement_timestamp: RedisNativeClient

    def __init__(self, client: Redis):
        self.client = client
        self.voting_enabled = RedisNativeClient(self.client, "voting_enabled")
        self.announcement_timestamp = RedisNativeClient(
            self.client, "announcement_timestamp"
        )
