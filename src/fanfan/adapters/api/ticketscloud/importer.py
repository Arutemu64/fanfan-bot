import logging

from fanfan.adapters.api.ticketscloud.client import TCloudClient
from fanfan.adapters.api.ticketscloud.config import TCloudConfig
from fanfan.adapters.api.ticketscloud.dto.order import Order, OrderStatus
from fanfan.adapters.api.ticketscloud.exceptions import NoTCloudConfigProvided
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
        config: TCloudConfig | None,
        client: TCloudClient | None,
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
        async with self.uow:
            for order_ticket in order.tickets:
                ticket = await self.tickets_repo.get_ticket_by_id(
                    TicketId(order_ticket.barcode)
                )
                if order.status == OrderStatus.DONE and ticket is None:
                    role = self.config.event_ids.get(order.event, UserRole.VISITOR)
                    ticket = Ticket(
                        id=TicketId(order_ticket.barcode),
                        role=role,
                        used_by_id=None,
                        issued_by_id=None,
                    )
                    await self.tickets_repo.add_ticket(ticket)
                    logger.info(
                        "New ticket %s was added", ticket.id, extra={"ticket": ticket}
                    )
                    added_tickets += 1
            await self.uow.commit()
        return added_tickets

    async def sync_tickets(self):
        if self.client is None:
            raise NoTCloudConfigProvided
        added_tickets = 0
        orders_init = await self.client.get_orders(page=1, page_size=DEFAULT_PAGE_SIZE)
        logger.info(
            "About to process %s orders from TicketsCloud",
            orders_init.total_count,
        )
        # Order
        for page in range(1, orders_init.pagination.total + 1):
            result = await self.client.get_orders(
                page=page, page_size=DEFAULT_PAGE_SIZE
            )
            for order_data in result.data:
                added_tickets += await self.proceed_order(order_data)
                logger.info(
                    "Ongoing import: %s tickets added",
                    added_tickets,
                )
        # Refunds
        # TODO TicketsCloud API fucking suck
        #  (no way to get barcode of refunded tickets
        #  without storing ticket ID/barcode pairs)
        #  Reimplement refunds later
