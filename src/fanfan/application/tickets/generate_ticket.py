import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.codes import CodesRepository
from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.models.code import Code
from fanfan.core.models.ticket import Ticket
from fanfan.core.services.tickets import TicketsService
from fanfan.core.utils.code import generate_unique_code
from fanfan.core.vo.code import CodeId
from fanfan.core.vo.ticket import TicketId
from fanfan.core.vo.user import UserRole

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class GenerateTicketDTO:
    role: UserRole = UserRole.VISITOR


@dataclass(frozen=True, slots=True)
class GenerateTicketResult:
    ticket_id: TicketId
    code_id: CodeId


class GenerateTicket:
    def __init__(
        self,
        tickets_repo: TicketsRepository,
        codes_repo: CodesRepository,
        uow: UnitOfWork,
        id_provider: IdProvider,
        service: TicketsService,
    ) -> None:
        self.tickets_repo = tickets_repo
        self.codes_repo = codes_repo
        self.uow = uow
        self.id_provider = id_provider
        self.service = service

    async def __call__(self, data: GenerateTicketDTO) -> GenerateTicketResult:
        user = await self.id_provider.get_user_data()
        self.service.ensure_user_can_create_tickets(user)

        # Generate ticket
        for _ in range(10):
            unique_code = generate_unique_code(length=8)
            async with self.uow:
                try:
                    ticket = Ticket(
                        id=TicketId(unique_code),
                        role=data.role,
                        used_by_id=None,
                        issued_by_id=user.id,
                    )
                    user_code = Code(
                        id=CodeId(unique_code),
                        achievement_id=None,
                        user_id=None,
                        ticket_id=ticket.id,
                    )
                    await self.tickets_repo.add_ticket(ticket)
                    await self.codes_repo.add_code(user_code)
                    await self.uow.commit()
                    break
                except IntegrityError:
                    await self.uow.rollback()

        logger.info("New ticket %s was created", ticket.id, extra={"ticket": ticket})
        return GenerateTicketResult(ticket_id=ticket.id, code_id=user_code.id)
