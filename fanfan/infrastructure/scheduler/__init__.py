import uuid
from datetime import timedelta
from typing import TYPE_CHECKING

from dishka.integrations.taskiq import setup_dishka
from taskiq import SimpleRetryMiddleware, TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from fanfan.common.config import get_config

if TYPE_CHECKING:
    from dishka import AsyncContainer

redis_async_result = RedisAsyncResultBackend(
    redis_url=get_config().redis.build_connection_str(),
    result_ex_time=timedelta(hours=1).seconds,
)

broker = (
    ListQueueBroker(
        url=get_config().redis.build_connection_str(),
    )
    .with_result_backend(redis_async_result)
    .with_middlewares(SimpleRetryMiddleware(default_retry_count=0))
    .with_id_generator(lambda: f"task:{uuid.uuid4().hex}")
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    from fanfan.infrastructure.di import create_scheduler_container

    container = create_scheduler_container()
    setup_dishka(container, broker)
    state.container = container


@broker.on_event(TaskiqEvents.WORKER_SHUTDOWN)
async def shutdown(state: TaskiqState) -> None:
    container: AsyncContainer = state.container
    await container.close()


scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
