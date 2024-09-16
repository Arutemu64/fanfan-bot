import logging

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.exceptions.tickets import (
    TicketAlreadyUsed,
    TicketNotFound,
    UserAlreadyHasTicketLinked,
)
from fanfan.core.exceptions.users import UserNotFound
from fanfan.infrastructure.db.models import Ticket, User

logger = logging.getLogger(__name__)


class LinkTicket:
    def __init__(
        self,
        session: AsyncSession,
    ) -> None:
        self.session = session

    async def __call__(self, ticket_id: str, user_id: int) -> None:
        async with self.session:
            ticket = await self.session.get(Ticket, ticket_id)
            if not ticket:
                raise TicketNotFound

            user = await self.session.get(User, user_id)
            if not user:
                raise UserNotFound

            try:
                user.ticket = ticket
                await self.session.commit()
                logger.info("Ticket %s was linked to user %s", ticket_id, user_id)
            except IntegrityError as e:
                await self.session.rollback()
                if ticket.used_by_id:
                    raise TicketAlreadyUsed from e
                if user.ticket:
                    raise UserAlreadyHasTicketLinked from e
