from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import Ticket
from fanfan.core.models.ticket import TicketId, TicketModel


class TicketsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_ticket(self, model: TicketModel) -> TicketModel:
        ticket = Ticket.from_model(model)
        self.session.add(ticket)
        await self.session.flush([ticket])
        return ticket.to_model()

    async def get_ticket_by_id(self, ticket_id: TicketId) -> TicketModel | None:
        ticket = await self.session.get(Ticket, ticket_id)
        return ticket.to_model() if ticket else None

    async def save_ticket(self, model: TicketModel) -> TicketModel:
        ticket = await self.session.merge(Ticket.from_model(model))
        await self.session.flush([ticket])
        return ticket.to_model()

    async def delete_ticket(self, ticket_id: TicketId) -> None:
        await self.session.execute(delete(Ticket).where(Ticket.id == ticket_id))
