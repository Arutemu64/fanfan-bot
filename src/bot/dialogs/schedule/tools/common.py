import time

from src.bot.structures import UserRole
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


async def check_permission(db: Database, user_id: int) -> bool:
    if await db.user.get_role(user_id) in [UserRole.HELPER, UserRole.ORG]:
        return True
    else:
        return False
