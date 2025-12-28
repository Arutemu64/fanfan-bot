import logging

from fanfan.adapters.api.ticketscloud.client import TCloudClient
from fanfan.adapters.api.ticketscloud.config import TCloudConfig
from fanfan.adapters.api.ticketscloud.dto.order import Order, OrderStatus
from fanfan.adapters.api.ticketscloud.dto.refund import Refund, RefundStatus
from fanfan.adapters.db.repositories.tickets import TicketsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.models.ticket import Ticket
from fanfan.core.services.tickets import TicketsService
from fanfan.core.vo.ticket import TicketId
from fanfan.core.vo.user import UserRole

logger = logging.getLogger(__name__)

DEFAULT_PAGE_SIZE = 200


class TCloudImporter:
    def __init__(
        self,
        config: TCloudConfig,
        client: TCloudClient,
        tickets_repo: TicketsRepository,
        tickets_service: TicketsService,
        uow: UnitOfWork,
    ):
        self.config = config
        self.client = client
        self.tickets_repo = tickets_repo
        self.tickets_service = tickets_service
        self.uow = uow

    async def proceed_order(self, order: Order) -> int:
        added_tickets = 0
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
                added_tickets += 1
        return added_tickets

    async def proceed_refund(self, refund: Refund) -> int:
        removed_tickets = 0
        for ticket_id in refund.tickets:
            ticket = await self.tickets_repo.get_ticket_by_external_id(ticket_id)
            if refund.status == RefundStatus.APPROVED and ticket:
                await self.tickets_repo.delete_ticket(ticket)
                logger.info(
                    "Ticket %s was refunded", ticket.id, extra={"ticket": ticket}
                )
                removed_tickets += 1
        return removed_tickets

    async def sync_tickets(self):
        added_tickets, removed_tickets = 0, 0
        orders_init = await self.client.get_orders(page=1, page_size=DEFAULT_PAGE_SIZE)
        refunds_init = await self.client.get_refunds(
            page=1, page_size=DEFAULT_PAGE_SIZE
        )
        logger.info(
            "About to process %s orders and %s refunds from TicketsCloud",
            orders_init.total_count,
            refunds_init.total_count,
        )
        # Orders
        for page in range(1, orders_init.pagination.total + 1):
            result = await self.client.get_orders(
                page=page, page_size=DEFAULT_PAGE_SIZE
            )
            async with self.uow:
                for order_data in result.data:
                    added_tickets += await self.proceed_order(order_data)
                    logger.info(
                        "Ongoing import: %s tickets added",
                        added_tickets,
                    )
                await self.uow.commit()
        # Refunds
        for page in range(1, refunds_init.pagination.total + 1):
            result = await self.client.get_refunds(
                page=page, page_size=DEFAULT_PAGE_SIZE
            )
            async with self.uow:
                for refunds_data in result.data:
                    removed_tickets += await self.proceed_refund(refunds_data)
                    logger.info(
                        "Ongoing import: %s tickets removed",
                        removed_tickets,
                    )
                await self.uow.commit()
