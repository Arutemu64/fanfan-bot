from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import DBQuote


class GetRandomQuote:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(self) -> str | None:
        query = select(DBQuote.text).order_by(func.random()).limit(1)
        return await self.session.scalar(query)
