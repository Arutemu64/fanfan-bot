from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models.quest_registration import QuestRegistration
from fanfan.core.models.user import UserId


class QuestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_registration(self, user_id: UserId) -> None:
        registration = QuestRegistration(user_id=user_id)
        self.session.add(registration)
        await self.session.flush([registration])

    async def count_registrations(self) -> int:
        return await self.session.scalar(select(func.count(QuestRegistration.id)))

    async def delete_user_registration(self, user_id: UserId):
        await self.session.execute(
            delete(QuestRegistration).where(QuestRegistration.user_id == user_id)
        )
