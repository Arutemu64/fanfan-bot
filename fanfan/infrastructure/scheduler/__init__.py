import uuid
from datetime import timedelta

from taskiq import SimpleRetryMiddleware, TaskiqScheduler
from taskiq.schedule_sources import LabelScheduleSource
from taskiq.serializers import ORJSONSerializer
from taskiq_redis import ListQueueBroker, RedisAsyncResultBackend

from fanfan.config import get_config

redis_async_result = RedisAsyncResultBackend(
    redis_url=get_config().redis.build_connection_str("1"),
    result_ex_time=timedelta(hours=1).seconds,
)

broker = (
    ListQueueBroker(
        url=get_config().redis.build_connection_str("1"),
    )
    .with_result_backend(redis_async_result)
    .with_serializer(ORJSONSerializer())
    .with_middlewares(SimpleRetryMiddleware(default_retry_count=0))
    .with_id_generator(lambda: f"task:{uuid.uuid4().hex}")
)

scheduler = TaskiqScheduler(
    broker=broker,
    sources=[LabelScheduleSource(broker)],
)
