from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import GlobalSettings


async def setup_initial_settings(session: AsyncSession) -> None:
    async with session:
        try:
            session.add(GlobalSettings(id=1))
            await session.commit()
        except IntegrityError:
            await session.rollback()
