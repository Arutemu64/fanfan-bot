from fanfan.adapters.db.repositories.achievements import AchievementsRepository
from fanfan.adapters.db.repositories.quest import QuestRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider


class ResetQuest:
    def __init__(
        self,
        achievements_repo: AchievementsRepository,
        quest_repo: QuestRepository,
        uow: UnitOfWork,
        id_provider: IdProvider,
    ):
        self.achievements_repo = achievements_repo
        self.quest_repo = quest_repo
        self.uow = uow
        self.id_provider = id_provider

    async def __call__(self) -> None:
        async with self.uow:
            participant = await self.quest_repo.get_player(
                user_id=self.id_provider.get_current_user_id()
            )
            participant.points = 0
            await self.quest_repo.save_player(participant)
            await self.achievements_repo.delete_all_user_received_achievements(
                user_id=self.id_provider.get_current_user_id()
            )
            await self.uow.commit()
