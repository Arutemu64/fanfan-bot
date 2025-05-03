import logging

from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.exceptions.tickets import TicketNotFound
from fanfan.core.models.ticket import TicketId

logger = logging.getLogger(__name__)


class DeleteTicket:
    def __init__(self, tickets_repo: TicketsRepository, uow: UnitOfWork) -> None:
        self.tickets_repo = tickets_repo
        self.uow = uow

    async def __call__(self, ticket_id: TicketId) -> None:
        ticket = await self.tickets_repo.get_ticket_by_id(ticket_id)
        if ticket is None:
            raise TicketNotFound
        async with self.uow:
            await self.tickets_repo.delete_ticket(ticket)
            await self.uow.commit()
            logger.info("Ticket %s was deleted", ticket_id, extra={"ticket": ticket})
            return
