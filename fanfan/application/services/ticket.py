import logging

from sqlalchemy.exc import IntegrityError

from fanfan.application.dto.ticket import CreateTicketDTO, TicketDTO
from fanfan.application.dto.user import UpdateUserDTO
from fanfan.application.exceptions.ticket import (
    TicketAlreadyExist,
    TicketAlreadyUsed,
    TicketNotFound,
    UserAlreadyHasTicketLinked,
)
from fanfan.application.exceptions.users import (
    UserNotFound,
)
from fanfan.application.services.base import BaseService

logger = logging.getLogger(__name__)


class TicketService(BaseService):
    async def create_ticket(self, dto: CreateTicketDTO) -> TicketDTO:
        """Create a new ticket"""
        async with self.uow:
            try:
                ticket = await self.uow.tickets.add_ticket(dto)
                await self.uow.commit()
                logger.info(f"New ticket id={ticket.id} was created")
                return ticket
            except IntegrityError:
                raise TicketAlreadyExist

    async def link_ticket(self, ticket_id: str, user_id: int) -> None:
        """Link a ticket to a user
        @return: UserDTO with a linked ticket
        """
        ticket = await self.uow.tickets.get_ticket(ticket_id)
        if not ticket:
            raise TicketNotFound
        async with self.uow:
            try:
                await self.uow.tickets.link_ticket(ticket_id, user_id)
                await self.uow.users.update_user(
                    UpdateUserDTO(id=user_id, role=ticket.role),
                )
                await self.uow.commit()
                logger.info(f"Ticket id={ticket_id} was linked to user id={user_id}")
                return
            except IntegrityError:
                await self.uow.rollback()
                if ticket.used_by_id:
                    raise TicketAlreadyUsed
                user = await self.uow.users.get_user_by_id(user_id)
                if not user:
                    raise UserNotFound
                if user.ticket:
                    raise UserAlreadyHasTicketLinked

    async def delete_ticket(self, ticket_id: str) -> None:
        async with self.uow:
            await self.uow.tickets.delete_ticket(ticket_id)
            await self.uow.commit()
            logger.info(f"Ticket id={ticket_id} was deleted")
            return
