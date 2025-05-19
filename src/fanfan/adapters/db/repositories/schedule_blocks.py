from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models.schedule_block import ScheduleBlockORM
from fanfan.core.models.schedule_block import ScheduleBlock


class ScheduleBlocksRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_block(self, block: ScheduleBlock) -> ScheduleBlock:
        block_orm = ScheduleBlockORM.from_model(block)
        self.session.add(block_orm)
        await self.session.flush([block_orm])
        return block_orm.to_model()

    async def delete_all_blocks(self):
        await self.session.execute(delete(ScheduleBlockORM))
        await self.session.flush()
