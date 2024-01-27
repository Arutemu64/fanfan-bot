from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.infrastructure.db.repositories.repo import Repository

from ..models import Ticket


class TicketsRepository(Repository[Ticket]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Ticket, session=session)

    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        return await self.session.get(Ticket, ticket_id)
