from dishka import FromDishka
from dishka.integrations.taskiq import inject

from fanfan.application.ticketscloud.sync_tcloud import SyncTCloud, SyncTCloudResult
from fanfan.main.scheduler import broker


@broker.task(task_name="sync_tcloud", schedule=[{"cron": "0 * * * *"}])
@inject
async def sync_tcloud(
    sync_tcloud: FromDishka[SyncTCloud],
) -> SyncTCloudResult:
    return await sync_tcloud()
