import asyncio
import contextlib
import logging
import sys

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.config.parsers import get_config
from fanfan.adapters.db.models import GlobalSettingsORM
from fanfan.common.logging import setup_logging
from fanfan.main.di import create_system_container

logger = logging.getLogger(__name__)


async def migrate():
    container = create_system_container()

    # Setup initial settings
    async with container() as container:
        session: AsyncSession = await container.get(AsyncSession)
        async with session:
            try:
                session.add(GlobalSettingsORM(id=1))
                await session.commit()
            except IntegrityError:
                await session.rollback()

    logger.info("Migration completed")


def main():
    config = get_config()
    setup_logging(
        level=config.debug.logging_level,
        json_logs=config.debug.json_logs,
    )
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(migrate())


if __name__ == "__main__":
    main()
