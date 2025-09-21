import asyncio
import contextlib
import logging

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.app_settings import SettingsRepository
from fanfan.adapters.db.repositories.permissions import PermissionsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.constants.permissions import Permissions
from fanfan.core.models.app_settings import AppSettings
from fanfan.core.models.permission import Permission
from fanfan.main.common import init
from fanfan.main.di import create_system_container

logger = logging.getLogger(__name__)


async def migrate():
    container = create_system_container()
    async with container() as container:
        uow = await container.get(UnitOfWork)

        # Add new permissions
        permissions_repo = await container.get(PermissionsRepository)
        for name in Permissions:
            try:
                await permissions_repo.add_permission(Permission(name=name))
                await uow.commit()
                logger.info("New permission added: %s", name)
            except IntegrityError:
                await uow.rollback()

        # Setup initial settings
        settings_repo = await container.get(SettingsRepository)
        try:
            await settings_repo.add_settings(AppSettings())
            await uow.commit()
        except IntegrityError:
            await uow.rollback()

    logger.info("Migration completed")


def main():
    init(service_name="migration")
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(migrate())


if __name__ == "__main__":
    main()
