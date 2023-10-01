from typing import Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Ticket
from .abstract import Repository


class TicketRepo(Repository[Ticket]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Ticket, session=session)

    async def new(
        self,
        id: str,
        role: str = "visitor",
        used_by: Optional[int] = None,
        issued_by: Optional[int] = None,
    ) -> Ticket:
        new_ticket = await self.session.merge(
            Ticket(id=id, role=role, used_by=used_by, issued_by=issued_by)
        )
        return new_ticket

    async def exists(self, ticket_id: str) -> Optional[Ticket]:
        return await super()._exists(func.lower(Ticket.id) == ticket_id.lower())

    async def get_count(self) -> int:
        return await super()._get_count()
