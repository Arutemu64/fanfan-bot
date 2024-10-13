import logging

from sqlalchemy.exc import IntegrityError

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.models.ticket import TicketId
from fanfan.infrastructure.db.repositories.tickets import TicketsRepository
from fanfan.infrastructure.db.uow import UnitOfWork

logger = logging.getLogger(__name__)


class LinkTicket(Interactor[TicketId, None]):
    def __init__(
        self, tickets_repo: TicketsRepository, uow: UnitOfWork, id_provider: IdProvider
    ) -> None:
        self.tickets_repo = tickets_repo
        self.uow = uow
        self.id_provider = id_provider

    async def __call__(self, ticket_id: TicketId) -> None:
        user_id = self.id_provider.get_current_user_id()
        async with self.uow:
            try:
                await self.tickets_repo.link_ticket_to_user(
                    ticket_id=ticket_id, user_id=user_id
                )
                await self.uow.commit()
            except IntegrityError:
                await self.uow.rollback()
                raise
            else:
                logger.info("Ticket %s was linked to user %s", ticket_id, user_id)
