from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.ticket import TicketDTO
from fanfan.application.exceptions.ticket import (
    TicketAlreadyExist,
    TicketAlreadyUsed,
    TicketNotFound,
    UserAlreadyHasTicketLinked,
)
from fanfan.application.exceptions.users import (
    UserServiceNotFound,
)
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.common.enums import UserRole
from fanfan.infrastructure.db.models import Ticket


class TicketService(BaseService):
    @check_permission(allowed_roles=[UserRole.ORG])
    async def create_ticket(self, ticket_id: str, role: UserRole) -> TicketDTO:
        """
        Create a new ticket
        """
        async with self.uow:
            try:
                ticket = Ticket(id=ticket_id, role=role)
                self.uow.session.add(ticket)
                await self.uow.commit()
                return ticket.to_dto()
            except IntegrityError:
                raise TicketAlreadyExist

    async def link_ticket(self, ticket_id: str, user_id: int) -> None:
        """
        Link a ticket to a user
        @return: UserDTO with a linked ticket
        """
        ticket = await self.uow.tickets.get_ticket(ticket_id)
        if not ticket:
            raise TicketNotFound
        if ticket.used_by_id:
            raise TicketAlreadyUsed
        user = await self.uow.users.get_user_by_id(user_id)
        if not user:
            raise UserServiceNotFound
        if user.ticket:
            raise UserAlreadyHasTicketLinked
        async with self.uow:
            user.ticket = ticket
            user.role = ticket.role
            await self.uow.commit()
            return user.to_full_dto()
