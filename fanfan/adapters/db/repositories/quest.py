from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import undefer

from fanfan.adapters.db.models import DBUser
from fanfan.core.models.quest import FullQuestParticipant, QuestParticipant
from fanfan.core.models.user import UserId


class QuestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_quest_participant(
        self, user_id: UserId, lock_points: bool = False
    ) -> FullQuestParticipant | None:
        query = (
            select(DBUser)
            .where(DBUser.id == user_id)
            .options(
                undefer(DBUser.achievements_count),
                undefer(DBUser.points),
            )
            .execution_options(populate_existing=True)
        )
        if lock_points:
            query = query.with_for_update(of=[DBUser.points])
        participant = await self.session.scalar(query)
        return (
            FullQuestParticipant(
                id=UserId(participant.id),
                points=participant.points,
                achievements_count=participant.achievements_count,
            )
            if participant
            else None
        )

    async def save_quest_participant(self, model: QuestParticipant) -> QuestParticipant:
        participant = await self.session.merge(DBUser(id=model.id, points=model.points))
        await self.session.flush([participant])
        return QuestParticipant(id=UserId(participant.id), points=participant.points)
