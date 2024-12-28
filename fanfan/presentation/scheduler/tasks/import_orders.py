from dishka import FromDishka
from dishka.integrations.taskiq import inject

from fanfan.application.utils.import_orders import (
    ImportOrders,
    ImportOrdersResult,
)
from fanfan.main.scheduler import broker


@broker.task(task_name="import_orders", schedule=[{"cron": "0 * * * *"}])
@inject
async def import_orders(
    interactor: FromDishka[ImportOrders],
) -> ImportOrdersResult:
    return await interactor()
