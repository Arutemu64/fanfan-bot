from dishka import FromDishka
from dishka.integrations.taskiq import inject

from fanfan.adapters.api.ticketscloud.importer import TCloudImporter
from fanfan.main.scheduler import broker


@broker.task(task_name="sync_tcloud", schedule=[{"cron": "0 * * * *"}])
@inject
async def sync_tcloud(
    importer: FromDishka[TCloudImporter],
) -> None:
    await importer.sync_tickets()
    return
