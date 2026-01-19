import logging

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.tickets import (
    TicketNotFound,
    UserAlreadyHasTicketLinked,
)
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.services.tickets import TicketsService
from fanfan.core.vo.ticket import TicketId

logger = logging.getLogger(__name__)


class UseTicket:
    def __init__(
        self,
        tickets_repo: TicketsRepository,
        tickets_service: TicketsService,
        uow: UnitOfWork,
        id_provider: IdProvider,
    ) -> None:
        self.tickets_repo = tickets_repo
        self.tickets_service = tickets_service
        self.uow = uow
        self.id_provider = id_provider

    async def __call__(self, ticket_id: TicketId) -> None:
        ticket = await self.tickets_repo.get_ticket_by_id(ticket_id)
        if ticket is None:
            raise TicketNotFound

        async with self.uow:
            try:
                user = await self.id_provider.get_current_user()
                await self.tickets_service.link_ticket(ticket=ticket, user=user)
                await self.uow.commit()
            except (IntegrityError, UserAlreadyHasTicketLinked, UserNotFound):
                await self.uow.rollback()
                raise
            else:
                logger.info(
                    "Ticket %s was linked to user %s",
                    ticket_id,
                    user.id,
                    extra={"user": user, "ticket": ticket},
                )
