import time

from src.config import conf
from src.db import Database

ANNOUNCEMENT_TIMEOUT = conf.bot.announcement_timeout


async def throttle_announcement(db: Database) -> bool:
    global_timestamp = await db.settings.get_announcement_timestamp()
    timestamp = time.time()
    if (timestamp - global_timestamp) < ANNOUNCEMENT_TIMEOUT:
        return False
    else:
        await db.settings.set_announcement_timestamp(timestamp)
        return True
