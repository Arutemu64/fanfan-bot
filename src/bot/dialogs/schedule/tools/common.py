import time

from src.bot.structures import Settings
from src.config import conf

ANNOUNCEMENT_TIMEOUT = conf.bot.announcement_timeout


async def throttle_announcement(settings: Settings):
    global_timestamp = await settings.announcement_timestamp.get()
    timestamp = time.time()
    if (timestamp - global_timestamp) < ANNOUNCEMENT_TIMEOUT:
        return False
    else:
        await settings.announcement_timestamp.set(timestamp)
        return True
