import datetime
import logging

from redis.asyncio import Redis
from taskiq import ScheduledTask

from fanfan.adapters.config_reader import Configuration
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.tasks import (
    TaskInProgress,
)
from fanfan.core.models.tasks import TaskStatus
from fanfan.main.scheduler import redis_schedule
from fanfan.presentation.scheduler.tasks.update_tickets import (
    UPDATE_TICKETS_LOCK,
    UPDATE_TICKETS_TIMESTAMP,
    update_tickets,
)

logger = logging.getLogger(__name__)


class TaskManager:
    def __init__(self, config: Configuration, redis: Redis, id_provider: IdProvider):
        self.config = config
        self.redis = redis
        self.id_provider = id_provider

    async def update_tickets(self) -> None:
        # Check permission
        user = await self.id_provider.get_current_user()
        if user.role != UserRole.ORG:
            raise AccessDenied
        # Check lock
        if await self.redis.lock(UPDATE_TICKETS_LOCK).locked():
            raise TaskInProgress
        # Run
        await update_tickets.kiq(by_user_id=user.id if user else None)

    async def get_update_tickets_status(self) -> TaskStatus:
        schedule = await redis_schedule.get_schedules()
        running = await self.redis.lock(UPDATE_TICKETS_LOCK).locked()
        timestamp = float(await self.redis.get(UPDATE_TICKETS_TIMESTAMP) or 0)
        last_execution = datetime.datetime.fromtimestamp(timestamp, datetime.UTC)
        cron = next((t.cron for t in schedule if t.task_name == "update_tickets"), None)
        return TaskStatus(running=running, last_execution=last_execution, cron=cron)

    @staticmethod
    async def set_task_cron(task_name: str, cron: str | None) -> None:
        if cron:
            await redis_schedule.add_schedule(
                ScheduledTask(
                    task_name=task_name,
                    schedule_id=task_name,
                    cron=cron,
                    labels={},
                    args=[],
                    kwargs={},
                )
            )
        else:
            await redis_schedule.delete_schedule(task_name)
