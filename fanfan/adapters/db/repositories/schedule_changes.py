from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import ScheduleChangeORM
from fanfan.core.models.schedule_change import (
    ScheduleChange,
    ScheduleChangeId,
)


class ScheduleChangesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_schedule_change(self, change: ScheduleChange) -> ScheduleChange:
        schedule_change_orm = ScheduleChangeORM.from_model(change)
        self.session.add(schedule_change_orm)
        await self.session.flush([schedule_change_orm])
        return schedule_change_orm.to_model()

    async def get_schedule_change(
        self, change_id: ScheduleChangeId
    ) -> ScheduleChange | None:
        stmt = select(ScheduleChangeORM).where(ScheduleChangeORM.id == change_id)
        schedule_change_orm = await self.session.scalar(stmt)
        return schedule_change_orm.to_model() if schedule_change_orm else None

    async def delete_schedule_change(self, change: ScheduleChange) -> None:
        await self.session.execute(
            delete(ScheduleChangeORM).where(ScheduleChangeORM.id == change.id)
        )
