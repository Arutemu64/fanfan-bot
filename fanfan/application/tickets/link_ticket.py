import logging

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.tickets import (
    TicketAlreadyUsed,
    TicketNotFound,
    UserAlreadyHasTicketLinked,
)
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.ticket import TicketId

logger = logging.getLogger(__name__)


class LinkTicket:
    def __init__(
        self,
        tickets_repo: TicketsRepository,
        users_repo: UsersRepository,
        uow: UnitOfWork,
        id_provider: IdProvider,
    ) -> None:
        self.tickets_repo = tickets_repo
        self.users_repo = users_repo
        self.uow = uow
        self.id_provider = id_provider

    async def __call__(self, ticket_id: TicketId) -> None:
        user_id = self.id_provider.get_current_user_id()
        async with self.uow:
            try:
                # Get user
                user = await self.users_repo.get_user_by_id(user_id)
                if user is None:
                    raise UserNotFound
                if user.ticket:
                    raise UserAlreadyHasTicketLinked

                # Get ticket
                ticket = await self.tickets_repo.get_ticket_by_id(ticket_id)
                if ticket is None:
                    raise TicketNotFound
                if ticket.used_by_id:
                    raise TicketAlreadyUsed

                # Link ticket
                ticket.used_by_id = user_id
                user.role = ticket.role
                await self.tickets_repo.save_ticket(ticket)
                await self.users_repo.save_user(user)
                await self.uow.commit()
            except IntegrityError:
                await self.uow.rollback()
                raise
            else:
                user = await self.users_repo.get_user_by_id(user_id)
                logger.info(
                    "Ticket %s was linked to user %s",
                    ticket_id,
                    user_id,
                    extra={"user": user, "ticket": ticket},
                )
