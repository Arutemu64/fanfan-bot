from typing import TypeVar, Generic, Type, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base

T = TypeVar("T")
Base = declarative_base()


class Requests(Generic[T]):

    type_model: Type[Base]
    session: AsyncSession

    def __init__(self, type_model: Type[Base], session: AsyncSession):
        self.type_model = type_model
        self.session = session

    @classmethod
    async def get_one(cls, session: AsyncSession, whereclause) -> T:
        db_query = await session.execute(select(cls).where(whereclause))
        result = db_query.scalar_one_or_none()
        return result

    @classmethod
    async def get_many(cls, session: AsyncSession, whereclause) -> List[T]:
        db_query = await session.execute(select(cls).where(whereclause))
        result = db_query.scalars().all()
        return result

    @classmethod
    async def get_range(cls, session: AsyncSession, start: int, end: int, sort_by) -> List[T]:
        db_query = await session.execute(select(cls).order_by(sort_by).slice(start, end))
        return db_query.scalars().all()

    @classmethod
    async def count(cls, session: AsyncSession, whereclause) -> int:
        db_query = await session.execute(select(func.count()).select_from(cls).where(whereclause))
        count = db_query.scalar()
        return count
