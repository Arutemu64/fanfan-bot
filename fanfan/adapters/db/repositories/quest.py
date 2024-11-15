from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, undefer

from fanfan.adapters.db.models import User
from fanfan.adapters.db.models.quest_registration import QuestRegistration
from fanfan.core.models.quest import FullQuestParticipantModel, QuestParticipantModel
from fanfan.core.models.user import UserId


class QuestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_registration(self, user_id: UserId) -> None:
        registration = QuestRegistration(user_id=user_id)
        self.session.add(registration)
        await self.session.flush([registration])

    async def get_quest_participant(
        self, user_id: UserId, lock_points: bool = False
    ) -> FullQuestParticipantModel | None:
        query = (
            select(User)
            .where(User.id == user_id)
            .options(
                joinedload(User.quest_registration),
                undefer(User.achievements_count),
                undefer(User.points),
            )
            .execution_options(populate_existing=True)
        )
        if lock_points:
            query = query.with_for_update(of=[User.points])
        participant = await self.session.scalar(query)
        return (
            FullQuestParticipantModel(
                id=UserId(participant.id),
                points=participant.points,
                achievements_count=participant.achievements_count,
                quest_registration=bool(participant.quest_registration),
            )
            if participant
            else None
        )

    async def save_quest_participant(
        self, model: QuestParticipantModel
    ) -> QuestParticipantModel:
        participant = await self.session.merge(User(id=model.id, points=model.points))
        await self.session.flush([participant])
        return QuestParticipantModel(
            id=UserId(participant.id), points=participant.points
        )

    async def count_registrations(self) -> int:
        return await self.session.scalar(select(func.count(QuestRegistration.id)))
