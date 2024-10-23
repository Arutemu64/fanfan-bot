import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.common.interactor import Interactor
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.tickets import TicketAlreadyExist
from fanfan.core.models.ticket import TicketId, TicketModel

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True)
class CreateTicketDTO:
    id: TicketId
    role: UserRole = UserRole.VISITOR


class CreateTicket(Interactor[CreateTicketDTO, TicketModel]):
    def __init__(
        self, tickets_repo: TicketsRepository, uow: UnitOfWork, id_provider: IdProvider
    ) -> None:
        self.tickets_repo = tickets_repo
        self.uow = uow
        self.id_provider = id_provider

    async def __call__(self, data: CreateTicketDTO) -> TicketModel:
        user = await self.id_provider.get_current_user()
        if user.role is not UserRole.ORG:
            raise AccessDenied
        async with self.uow:
            try:
                ticket = await self.tickets_repo.add_ticket(
                    TicketModel(
                        id=data.id,
                        role=data.role,
                        issued_by_id=user.id,
                    )
                )
                await self.uow.commit()
            except IntegrityError as e:
                raise TicketAlreadyExist from e
            else:
                logger.info(
                    "New ticket %s was created", ticket.id, extra={"ticket": ticket}
                )
                return ticket
