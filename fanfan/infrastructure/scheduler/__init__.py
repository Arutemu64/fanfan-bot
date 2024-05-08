import uuid
from datetime import timedelta

from dishka import AsyncContainer, make_async_container
from dishka.integrations.taskiq import setup_dishka
from taskiq import SimpleRetryMiddleware, TaskiqEvents, TaskiqScheduler, TaskiqState
from taskiq.schedule_sources import LabelScheduleSource
from taskiq.serializers import ORJSONSerializer
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from fanfan.config import get_config

redis_async_result = RedisAsyncResultBackend(
    redis_url=get_config().redis.build_connection_str(),
    result_ex_time=timedelta(hours=1).seconds,
)

broker = (
    ListQueueBroker(
        url=get_config().redis.build_connection_str(),
    )
    .with_result_backend(redis_async_result)
    .with_serializer(ORJSONSerializer())
    .with_middlewares(SimpleRetryMiddleware(default_retry_count=0))
    .with_id_generator(lambda: f"task:{uuid.uuid4().hex}")
)


@broker.on_event(TaskiqEvents.WORKER_STARTUP)
async def startup(state: TaskiqState) -> None:
    from fanfan.infrastructure.di import get_app_providers

    container = make_async_container(*get_app_providers())
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
