from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import ContestEntryORM
from fanfan.core.models.contest import ContestEntry, ContestEntryId
from fanfan.core.models.user import UserId


class ContestRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_contest_entry(self, model: ContestEntry) -> ContestEntry:
        contest_entry = ContestEntryORM.from_model(model)
        self.session.add(contest_entry)
        await self.session.flush([contest_entry])
        return contest_entry.to_model()

    async def get_user_contest_entry(
        self, user_id: UserId, contest_name: str
    ) -> ContestEntry | None:
        query = select(ContestEntryORM).where(
            and_(
                ContestEntryORM.user_id == user_id,
                ContestEntryORM.contest_name == contest_name,
            )
        )
        contest_entry = await self.session.scalar(query)
        return contest_entry.to_model() if contest_entry else None

    async def delete_contest_entry(self, contest_entry_id: ContestEntryId) -> None:
        await self.session.execute(
            delete(ContestEntryORM).where(ContestEntryORM.id == contest_entry_id)
        )
