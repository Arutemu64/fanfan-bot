import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.core.enums import UserRole
from fanfan.core.exceptions.tickets import TicketAlreadyExist
from fanfan.core.models.ticket import TicketDTO
from fanfan.infrastructure.db.models import Ticket

logger = logging.getLogger(__name__)


@dataclass
class CreateTicketDTO:
    id: str
    role: UserRole


class CreateTicket:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def __call__(self, dto: CreateTicketDTO) -> TicketDTO:
        async with self.session:
            try:
                ticket = Ticket(id=dto.id, role=dto.role)
                self.session.add(ticket)
                await self.session.commit()
                logger.info("New ticket %s was created", dto.id)
                return ticket.to_dto()
            except IntegrityError as e:
                raise TicketAlreadyExist from e
