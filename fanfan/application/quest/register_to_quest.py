import logging

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.quest import AlreadyRegistered
from fanfan.core.services.access import AccessService

logger = logging.getLogger(__name__)


class RegisterToQuest:
    def __init__(
        self,
        quest_repo: QuestRepository,
        access: AccessService,
        uow: UnitOfWork,
        id_provider: IdProvider,
    ):
        self.quest_repo = quest_repo
        self.access = access
        self.uow = uow
        self.id_provider = id_provider

    async def __call__(self) -> None:
        await self.access.ensure_quest_registration_is_open()
        user = await self.id_provider.get_current_user()
        await self.access.ensure_can_participate_in_quest(user)
        async with self.uow:
            try:
                await self.quest_repo.add_registration(user_id=user.id)
                await self.uow.commit()
            except IntegrityError as e:
                raise AlreadyRegistered from e
            else:
                logger.info(
                    "User %s has registered to quest",
                    self.id_provider.get_current_user_id(),
                )
