import asyncio
import contextlib
import logging
import sys

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.config.parsers import get_config
from fanfan.adapters.db.models import DBGlobalSettings
from fanfan.common.logging import setup_logging
from fanfan.main.di import create_scheduler_container

logger = logging.getLogger(__name__)


async def migrate():
    container = create_scheduler_container()

    # Setup initial settings
    async with container() as container:
        session: AsyncSession = await container.get(AsyncSession)
        async with session:
            try:
                session.add(DBGlobalSettings(id=1))
                await session.commit()
            except IntegrityError:
                await session.rollback()

    logger.info("Migration completed")


if __name__ == "__main__":
    config = get_config()
    setup_logging(
        level=config.debug.logging_level,
        json_logs=config.debug.json_logs,
    )
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(migrate())
