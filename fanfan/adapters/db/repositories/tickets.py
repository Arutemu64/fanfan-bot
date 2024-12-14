from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import DBTicket
from fanfan.core.models.ticket import Ticket, TicketId


class TicketsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_ticket(self, model: Ticket) -> Ticket:
        ticket = DBTicket.from_model(model)
        self.session.add(ticket)
        await self.session.flush([ticket])
        return ticket.to_model()

    async def get_ticket_by_id(self, ticket_id: TicketId) -> Ticket | None:
        ticket = await self.session.get(DBTicket, ticket_id)
        return ticket.to_model() if ticket else None

    async def save_ticket(self, model: Ticket) -> Ticket:
        ticket = await self.session.merge(DBTicket.from_model(model))
        await self.session.flush([ticket])
        return ticket.to_model()

    async def delete_ticket(self, ticket_id: TicketId) -> None:
        await self.session.execute(delete(DBTicket).where(DBTicket.id == ticket_id))
