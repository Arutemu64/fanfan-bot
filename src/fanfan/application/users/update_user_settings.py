import logging

from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider

logger = logging.getLogger(__name__)


class UpdateUserSettings:
    def __init__(
        self, users_repo: UsersRepository, id_provider: IdProvider, uow: UnitOfWork
    ):
        self.users_repo = users_repo
        self.id_provider = id_provider
        self.uow = uow

    async def set_items_per_page(self, items_per_page: int) -> None:
        user = await self.id_provider.get_current_user()
        async with self.uow:
            user.settings.items_per_page = items_per_page
            await self.users_repo.save_user(user)
            await self.uow.commit()

    async def set_receive_all_announcements(
        self, receive_all_announcements: bool
    ) -> None:
        user = await self.id_provider.get_current_user()
        async with self.uow:
            user.settings.receive_all_announcements = receive_all_announcements
            await self.users_repo.save_user(user)
            await self.uow.commit()
