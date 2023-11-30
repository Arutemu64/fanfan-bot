from typing import Optional

from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession

from ...bot.structures import UserRole
from ..models import DBUser, Ticket
from .abstract import Repository


class TicketRepo(Repository[Ticket]):
    def __init__(self, session: AsyncSession):
        super().__init__(type_model=Ticket, session=session)

    async def new(
        self,
        id: str,
        role: UserRole = UserRole.VISITOR,
        used_by: Optional[DBUser] = None,
        issued_by: Optional[DBUser] = None,
    ) -> Ticket:
        new_ticket = await self.session.merge(
            Ticket(id=id, role=role, used_by=used_by, issued_by=issued_by)
        )
        return new_ticket

    async def get(self, ticket_id: str) -> Optional[Ticket]:
        return await super()._get_by_where(func.lower(Ticket.id) == ticket_id.lower())
