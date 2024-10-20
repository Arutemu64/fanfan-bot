import logging

from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider

logger = logging.getLogger(__name__)


class CancelRegistration:
    def __init__(
        self, quest_repo: QuestRepository, uow: UnitOfWork, id_provider: IdProvider
    ):
        self.quest_repo = quest_repo
        self.id_provider = id_provider
        self.uow = uow

    async def __call__(self) -> None:
        async with self.uow:
            await self.quest_repo.delete_user_registration(
                user_id=self.id_provider.get_current_user_id()
            )
            await self.uow.commit()
            logger.info(
                "User %s cancelled their quest registration",
                self.id_provider.get_current_user_id(),
            )
