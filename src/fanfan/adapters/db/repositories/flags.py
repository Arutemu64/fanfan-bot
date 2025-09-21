from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import FlagORM
from fanfan.core.models.flag import Flag
from fanfan.core.vo.user import UserId


class FlagsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_flag(self, flag: Flag) -> Flag:
        flag_orm = FlagORM.from_model(flag)
        self.session.add(flag_orm)
        await self.session.flush([flag_orm])
        return flag_orm.to_model()

    async def get_flag_by_user(self, user_id: UserId, flag_name: str) -> Flag | None:
        stmt = select(FlagORM).where(
            and_(
                FlagORM.user_id == user_id,
                FlagORM.name == flag_name,
            )
        )
        flag_orm = await self.session.scalar(stmt)
        return flag_orm.to_model() if flag_orm else None

    async def delete_flag(self, flag: Flag) -> None:
        await self.session.execute(delete(FlagORM).where(FlagORM.id == flag.id))
