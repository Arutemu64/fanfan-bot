import time

from src.db import Database
from src.db.models import Settings


async def throttle_announcement(db: Database, settings: Settings) -> int:
    timestamp = time.time()
    if (timestamp - settings.announcement_timestamp) < settings.announcement_timeout:
        return int(
            settings.announcement_timestamp + settings.announcement_timeout - timestamp
        )
    else:
        settings.announcement_timestamp = timestamp
        await db.session.commit()
        return 0
