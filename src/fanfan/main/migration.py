import asyncio
import contextlib
import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import GlobalSettingsORM
from fanfan.adapters.db.repositories.permissions import PermissionsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.models.permission import Permission, PermissionsList
from fanfan.main.common import init
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
                logger.info("New permission added: %s", name)
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
    init(service_name="migration")
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(migrate())


if __name__ == "__main__":
    main()
