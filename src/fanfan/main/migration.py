import asyncio
import contextlib
import logging
import sys

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.config.parsers import get_config
from fanfan.adapters.db.models import GlobalSettingsORM
from fanfan.adapters.db.repositories.permissions import PermissionsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.debug.logging import setup_logging
from fanfan.adapters.debug.telemetry import setup_telemetry
from fanfan.core.models.permission import Permission, PermissionsList
from fanfan.main.di import create_system_container

logger = logging.getLogger(__name__)


async def migrate():
    container = create_system_container()
    async with container() as container:
        uow = await container.get(UnitOfWork)

        # Add new permissions
        permissions_repo = await container.get(PermissionsRepository)
        for name in PermissionsList:
            try:
                await permissions_repo.add_permission(Permission(name=name))
                await uow.commit()
                logger.info(f"New permission added: {name}")
            except IntegrityError:
                await uow.rollback()

        # Setup initial settings
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
    setup_telemetry(
        service_name="migration",
        environment=config.env,
        logfire_token=config.debug.logfire_token.get_secret_value()
        if config.debug.logfire_token
        else None,
    )
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(migrate())


if __name__ == "__main__":
    main()
