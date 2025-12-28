import uuid
from datetime import timedelta
from typing import TYPE_CHECKING

from dishka.integrations.taskiq import setup_dishka
from taskiq import SimpleRetryMiddleware, TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import RedisAsyncResultBackend, RedisStreamBroker

from fanfan.adapters.config.parsers import get_config
from fanfan.main.common import init

if TYPE_CHECKING:
    from dishka import AsyncContainer

redis_async_result = RedisAsyncResultBackend(
    redis_url=get_config().redis.build_connection_str(),
    result_ex_time=timedelta(hours=2).seconds,
)
broker = (
    RedisStreamBroker(
        url=get_config().redis.build_connection_str(),
    )
    .with_result_backend(redis_async_result)
    .with_middlewares(SimpleRetryMiddleware(default_retry_count=0))
    .with_id_generator(lambda: f"task:{uuid.uuid4().hex}")
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    init(service_name="taskiq")

    from fanfan.main.di import create_system_container  # noqa: PLC0415

    container = create_system_container()

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
