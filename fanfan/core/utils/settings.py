from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.infrastructure.db.models import Settings


async def setup_initial_settings(session: AsyncSession) -> None:
    async with session:
        try:
            session.add(Settings(id=1))
            await session.commit()
        except IntegrityError:
            await session.rollback()
