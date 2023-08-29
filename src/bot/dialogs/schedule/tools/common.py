import time

from src.config import conf
from src.redis.global_settings import GlobalSettings

ANNOUNCEMENT_TIMEOUT = conf.bot.announcement_timeout


async def throttle_announcement(settings: GlobalSettings):
    global_timestamp = await settings.announcement_timestamp.get()
    timestamp = time.time()
    if (timestamp - global_timestamp) < ANNOUNCEMENT_TIMEOUT:
        return False
    else:
        await settings.announcement_timestamp.set(timestamp)
        return True
