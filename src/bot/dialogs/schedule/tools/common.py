import time

from src.bot.structures import UserRole
from src.config import conf
from src.db import Database
from src.redis.global_settings import GlobalSettings

ANNOUNCEMENT_TIMEOUT = conf.bot.announcement_timeout


async def throttle_announcement(settings: GlobalSettings) -> bool:
    global_timestamp = await settings.announcement_timestamp.get()
    timestamp = time.time()
    if (timestamp - global_timestamp) < ANNOUNCEMENT_TIMEOUT:
        return False
    else:
        await settings.announcement_timestamp.set(timestamp)
        return True


async def check_permission(db: Database, user_id: int) -> bool:
    if await db.user.get_role(user_id) in [UserRole.HELPER, UserRole.ORG]:
        return True
    else:
        return False
