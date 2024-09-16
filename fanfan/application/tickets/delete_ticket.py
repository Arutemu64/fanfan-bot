import logging

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.infrastructure.db.models import Ticket

logger = logging.getLogger(__name__)


class DeleteTicket:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def __call__(self, ticket_id: str) -> None:
        async with self.session:
            await self.session.execute(delete(Ticket).where(Ticket.id == ticket_id))
            await self.session.commit()
            logger.info("Ticket %s was deleted", ticket_id)
            return
