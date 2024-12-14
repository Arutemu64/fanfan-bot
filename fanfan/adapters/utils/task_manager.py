import logging

from fanfan.adapters.config.models import Configuration
from fanfan.adapters.utils.limit import LimitFactory
from fanfan.application.common.id_provider import IdProvider
from fanfan.application.utils.import_from_c2 import IMPORT_FROM_C2_LIMIT_NAME
from fanfan.application.utils.import_orders import IMPORT_ORDERS_LIMIT_NAME
from fanfan.core.dto.tasks import TaskStatus
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.limiter import (
    LimitLocked,
)
from fanfan.core.models.user import UserRole
from fanfan.presentation.scheduler.tasks.import_from_c2 import import_from_c2
from fanfan.presentation.scheduler.tasks.import_orders import (
    import_orders,
)

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(
        self, config: Configuration, limiter: LimitFactory, id_provider: IdProvider
    ):
        self.config = config
        self.limiter = limiter
        self.id_provider = id_provider

    async def import_orders(self) -> None:
        limiter = self.limiter(IMPORT_ORDERS_LIMIT_NAME)
        # Check permission
        user = await self.id_provider.get_current_user()
        if user.role != UserRole.ORG:
            raise AccessDenied
        # Check lock
        if await limiter.locked():
            raise LimitLocked
        # Run
        await import_orders.kiq(by_user_id=user.id)

    async def import_from_c2(self) -> None:
        limiter = self.limiter(IMPORT_FROM_C2_LIMIT_NAME)
        # Check permission
        user = await self.id_provider.get_current_user()
        if user.role != UserRole.ORG:
            raise AccessDenied
        # Check lock
        if await limiter.locked():
            raise LimitLocked
        # Run
        await import_from_c2.kiq(by_user_id=user.id)

    async def get_import_orders_status(self) -> TaskStatus:
        limiter = self.limiter(IMPORT_ORDERS_LIMIT_NAME)
        running = await limiter.locked()
        last_execution = await limiter.get_last_execution()
        return TaskStatus(running=running, last_execution=last_execution)

    async def get_import_from_c2_status(self) -> TaskStatus:
        limiter = self.limiter(IMPORT_FROM_C2_LIMIT_NAME)
        running = await limiter.locked()
        last_execution = await limiter.get_last_execution()
        return TaskStatus(running=running, last_execution=last_execution)
