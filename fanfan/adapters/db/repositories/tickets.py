from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import TicketORM
from fanfan.core.models.ticket import Ticket, TicketId


class TicketsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_ticket(self, model: Ticket) -> Ticket:
        ticket = TicketORM.from_model(model)
        self.session.add(ticket)
        await self.session.flush([ticket])
        return ticket.to_model()

    async def get_ticket_by_id(self, ticket_id: TicketId) -> Ticket | None:
        ticket = await self.session.get(TicketORM, ticket_id)
        return ticket.to_model() if ticket else None

    async def save_ticket(self, model: Ticket) -> Ticket:
        ticket = await self.session.merge(TicketORM.from_model(model))
        await self.session.flush([ticket])
        return ticket.to_model()

    async def delete_ticket(self, ticket_id: TicketId) -> None:
        await self.session.execute(delete(TicketORM).where(TicketORM.id == ticket_id))
