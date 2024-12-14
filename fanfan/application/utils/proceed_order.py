import logging
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.timepad.dto.order import OrderStatus, RegistrationOrderResponse
from fanfan.adapters.timepad.exceptions import TimepadOrderProcessFailed
from fanfan.core.models.ticket import Ticket, TicketId
from fanfan.core.models.user import UserRole

logger = logging.getLogger(__name__)

PARTICIPANT_NOMINATIONS = [
    "Участник сценической программы",
    "Участник не сценических конкурсов",
]
GOOD_STATUSES = [
    OrderStatus.PAID,
    OrderStatus.OK,
    OrderStatus.PAID_OFFLINE,
    OrderStatus.PAID_UR,
]


@dataclass(slots=True, frozen=True)
class ProceedOrderResult:
    added_tickets: int
    deleted_tickets: int


class ProceedOrder:
    def __init__(self, tickets_repo: TicketsRepository, uow: UnitOfWork):
        self.tickets_repo = tickets_repo
        self.uow = uow

    async def __call__(self, data: RegistrationOrderResponse) -> ProceedOrderResult:
        added_tickets, deleted_tickets = 0, 0
        try:
            async with self.uow:
                for ticket in data.tickets:
                    existing_ticket = await self.tickets_repo.get_ticket_by_id(
                        TicketId(ticket.number)
                    )
                    if (data.status.name in GOOD_STATUSES) and (
                        existing_ticket is None
                    ):
                        await self.tickets_repo.add_ticket(
                            Ticket(
                                id=TicketId(ticket.number),
                                role=UserRole.PARTICIPANT
                                if ticket.ticket_type.name in PARTICIPANT_NOMINATIONS
                                else UserRole.VISITOR,
                                used_by_id=None,
                                issued_by_id=None,
                            )
                        )
                        added_tickets += 1
                    elif (data.status.name not in GOOD_STATUSES) and existing_ticket:
                        await self.tickets_repo.delete_ticket(TicketId(ticket.number))
                        deleted_tickets += 1
                await self.uow.commit()
            logger.info("Timepad order %s processed", data.id, extra={"order": data})
            return ProceedOrderResult(added_tickets, deleted_tickets)
        except IntegrityError as e:
            raise TimepadOrderProcessFailed from e
