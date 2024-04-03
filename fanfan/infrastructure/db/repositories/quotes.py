from typing import Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.infrastructure.db.models import Quote
from fanfan.infrastructure.db.repositories.repo import Repository


class QuotesRepository(Repository[Quote]):

    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Quote, session=session)

    async def get_random_quote(self) -> Optional[str]:
        query = select(Quote.text).order_by(func.random()).limit(1)
        return await self.session.scalar(query)
