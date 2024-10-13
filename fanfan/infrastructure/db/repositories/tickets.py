from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from fanfan.core.exceptions.tickets import (
    TicketAlreadyUsed,
    TicketNotFound,
    UserAlreadyHasTicketLinked,
)
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.ticket import TicketId, TicketModel
from fanfan.core.models.user import UserId
from fanfan.infrastructure.db.models import Ticket, User


class TicketsRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def add_ticket(self, model: TicketModel) -> TicketModel:
        ticket = Ticket(id=model.id, role=model.role)
        self.session.add(ticket)
        await self.session.flush([ticket])
        return ticket.to_model()

    async def get_ticket_by_id(self, ticket_id: TicketId) -> TicketModel | None:
        ticket = await self.session.get(Ticket, ticket_id)
        return ticket.to_model() if ticket else None

    async def link_ticket_to_user(self, ticket_id: TicketId, user_id: UserId) -> None:
        ticket = await self.session.get(Ticket, ticket_id)
        if ticket is None:
            raise TicketNotFound
        if ticket.used_by_id:
            raise TicketAlreadyUsed

        user = await self.session.get(User, user_id, options=[joinedload(User.ticket)])
        if user is None:
            raise UserNotFound
        if user.ticket:
            raise UserAlreadyHasTicketLinked

        user.ticket = ticket
        user.role = ticket.role
        await self.session.flush([user])

    async def delete_ticket(self, ticket_id: TicketId) -> None:
        await self.session.execute(delete(Ticket).where(Ticket.id == ticket_id))
