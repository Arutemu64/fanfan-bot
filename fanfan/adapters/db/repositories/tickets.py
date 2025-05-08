from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.db.models import TicketORM
from fanfan.core.models.ticket import Ticket, TicketId


class TicketsWriter:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_ticket(self, ticket: Ticket) -> Ticket:
        ticket_orm = TicketORM.from_model(ticket)
        self.session.add(ticket_orm)
        await self.session.flush([ticket_orm])
        return ticket_orm.to_model()

    async def get_ticket_by_id(self, ticket_id: TicketId) -> Ticket | None:
        stmt = select(TicketORM).where(TicketORM.id == ticket_id)
        ticket_orm = await self.session.scalar(stmt)
        return ticket_orm.to_model() if ticket_orm else None

    async def save_ticket(self, ticket: Ticket) -> Ticket:
        ticket_orm = await self.session.merge(TicketORM.from_model(ticket))
        await self.session.flush([ticket_orm])
        return ticket_orm.to_model()

    async def delete_ticket(self, ticket: Ticket) -> None:
        await self.session.execute(delete(TicketORM).where(TicketORM.id == ticket.id))
