from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.repositories.repo import Repository

from ..models import Ticket


class TicketsRepository(Repository[Ticket]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Ticket, session=session)

    async def create_ticket(self, ticket_id: str, role: UserRole) -> Ticket:
        ticket = Ticket(id=ticket_id, role=role)
        self.session.add(ticket)
        return ticket

    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        query = (
            select(Ticket).where(func.lower(Ticket.id) == ticket_id.lower()).limit(1)
        )
        return await self.session.scalar(query)

    # async def get(self, ticket_id: str) -> Optional[Ticket]:
    #     return await super()._get_by_where(func.lower(Ticket.id) == ticket_id.lower())
    #
    # async def new(
    #     self,
    #     ticket_id: str,
    #     role: UserRole = UserRole.VISITOR,
    #     used_by: Optional[DBUser] = None,
    #     issued_by: Optional[DBUser] = None,
    # ) -> Ticket:
    #     new_ticket = await self.session.merge(
    #         Ticket(id=ticket_id, role=role, used_by=used_by, issued_by=issued_by)
    #     )
    #     return new_ticket
