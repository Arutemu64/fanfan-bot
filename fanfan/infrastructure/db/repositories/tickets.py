from typing import Optional

from sqlalchemy import delete, update
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.application.dto.ticket import CreateTicketDTO, TicketDTO
from fanfan.infrastructure.db.repositories.repo import Repository

from ..models import Ticket


class TicketsRepository(Repository[Ticket]):
    def __init__(self, session: AsyncSession):
        self.session = session
        super().__init__(type_model=Ticket, session=session)

    async def add_ticket(self, dto: CreateTicketDTO) -> TicketDTO:
        ticket = Ticket(**dto.model_dump())
        self.session.add(ticket)
        await self.session.flush([ticket])
        return ticket.to_dto()

    async def get_ticket(self, ticket_id: str) -> Optional[Ticket]:
        return await self.session.get(Ticket, ticket_id)

    async def link_ticket(self, ticket_id: str, user_id: int) -> None:
        await self.session.execute(
            update(Ticket).where(Ticket.id == ticket_id).values(used_by_id=user_id)
        )

    async def delete_ticket(self, ticket_id: str) -> None:
        await self.session.execute(delete(Ticket).where(Ticket.id == ticket_id))
