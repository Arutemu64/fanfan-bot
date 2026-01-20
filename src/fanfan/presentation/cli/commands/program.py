import logging
from typing import TYPE_CHECKING, BinaryIO

import click
from dishka.integrations.click import CONTAINER_NAME

from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.parsers import parse_schedule
from fanfan.application.cosplay2.sync_cosplay2 import SyncCosplay2
from fanfan.presentation.cli.commands.common import async_command

if TYPE_CHECKING:
    from dishka import AsyncContainer

logger = logging.getLogger(__name__)


@click.command(name="sync_cosplay2")
@click.pass_context
@async_command
async def sync_cosplay2_command(context: click.Context):
    container: AsyncContainer = context.meta[CONTAINER_NAME]
    async with container() as r_container:
        sync_cosplay2 = await r_container.get(SyncCosplay2)
        await sync_cosplay2()
        logger.info("Importing from C2 done!")


@click.command(name="parse_schedule")
@click.argument("schedule", type=click.File("rb"))
@click.pass_context
@async_command
async def parse_schedule_command(context: click.Context, schedule: BinaryIO):
    container: AsyncContainer = context.meta[CONTAINER_NAME]
    async with container() as r_container:
        await parse_schedule(
            file=schedule,
            events_repo=await r_container.get(ScheduleEventsRepository),
            uow=await r_container.get(UnitOfWork),
        )
