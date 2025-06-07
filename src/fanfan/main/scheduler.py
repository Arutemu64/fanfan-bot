import uuid
from datetime import timedelta
from typing import TYPE_CHECKING

from dishka.integrations.taskiq import setup_dishka
from taskiq import SimpleRetryMiddleware, TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from fanfan.adapters.config.models import Configuration
from fanfan.adapters.config.parsers import get_config
from fanfan.adapters.debug.logging import setup_logging
from fanfan.adapters.debug.telemetry import setup_telemetry

if TYPE_CHECKING:
    from dishka import AsyncContainer

redis_async_result = RedisAsyncResultBackend(
    redis_url=get_config().redis.build_connection_str(),
    result_ex_time=timedelta(hours=2).seconds,
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
    from fanfan.main.di import create_system_container

    container = create_system_container()
    config: Configuration = await container.get(Configuration)

    setup_logging(
        level=config.debug.logging_level,
        json_logs=config.debug.json_logs,
    )
    setup_telemetry(
        service_name="scheduler",
        environment=config.env,
        logfire_token=config.debug.logfire_token.get_secret_value()
        if config.debug.logfire_token
        else None,
    )

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
