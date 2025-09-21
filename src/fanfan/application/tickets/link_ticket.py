import logging

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.repositories.users import UsersRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.tickets import (
    TicketNotFound,
    UserAlreadyHasTicketLinked,
)
from fanfan.core.vo.ticket import TicketId

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
        user = await self.id_provider.get_current_user()
        ticket = await self.tickets_repo.get_ticket_by_user_id(user.id)
        async with self.uow:
            try:
                if ticket:
                    raise UserAlreadyHasTicketLinked

                # Get ticket
                ticket = await self.tickets_repo.get_ticket_by_id(ticket_id)
                if ticket is None:
                    raise TicketNotFound

                # Link ticket
                ticket.set_as_used(user.id)
                user.set_role(ticket.role)
                await self.tickets_repo.save_ticket(ticket)
                await self.users_repo.save_user(user)
                await self.uow.commit()
            except IntegrityError:
                await self.uow.rollback()
                raise
            else:
                user = await self.users_repo.get_user_by_id(user.id)
                logger.info(
                    "Ticket %s was linked to user %s",
                    ticket_id,
                    user.id,
                    extra={"user": user, "ticket": ticket},
                )
