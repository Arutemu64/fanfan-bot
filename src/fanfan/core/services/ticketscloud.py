import logging

from fanfan.adapters.api.ticketscloud.client import TCloudClient
from fanfan.adapters.api.ticketscloud.config import TCloudConfig
from fanfan.adapters.api.ticketscloud.dto.order import Order, OrderStatus
from fanfan.adapters.api.ticketscloud.dto.refund import Refund, RefundStatus
from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.core.models.ticket import Ticket
from fanfan.core.services.tickets import TicketsService
from fanfan.core.vo.ticket import TicketId
from fanfan.core.vo.user import UserRole

logger = logging.getLogger(__name__)


class TCloudService:
    def __init__(
        self,
        config: TCloudConfig,
        client: TCloudClient,
        tickets_repo: TicketsRepository,
        tickets_service: TicketsService,
    ):
        self.config = config
        self.client = client
        self.tickets_repo = tickets_repo
        self.tickets_service = tickets_service

    async def proceed_order(self, order: Order) -> int:
        new_tickets_count = 0
        for order_ticket in order.tickets:
            ticket = await self.tickets_repo.get_ticket_by_external_id(order_ticket.id)
            if order.status == OrderStatus.DONE and ticket is None:
                role = self.config.event_ids.get(order.event, UserRole.VISITOR)
                ticket = Ticket(
                    id=TicketId(order_ticket.barcode),
                    external_id=order_ticket.id,
                    role=role,
                    used_by_id=None,
                    issued_by_id=None,
                )
                await self.tickets_repo.add_ticket(ticket)
                logger.info(
                    "New ticket %s was added", ticket.id, extra={"ticket": ticket}
                )
                new_tickets_count += 1
        return new_tickets_count

    async def proceed_refund(self, refund: Refund) -> int:
        removed_tickets_count = 0
        for ticket_id in refund.tickets:
            ticket = await self.tickets_repo.get_ticket_by_external_id(ticket_id)
            if refund.status == RefundStatus.APPROVED and ticket:
                await self.tickets_service.unlink_ticket(ticket)
                await self.tickets_repo.delete_ticket(ticket)
                logger.info(
                    "Ticket %s was refunded", ticket.id, extra={"ticket": ticket}
                )
                removed_tickets_count += 1
        return removed_tickets_count
