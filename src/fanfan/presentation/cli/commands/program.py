import logging
from typing import TYPE_CHECKING, BinaryIO

import click
from dishka.integrations.click import CONTAINER_NAME

from fanfan.adapters.api.cosplay2.importer import Cosplay2Importer
from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.utils.parsers.parse_schedule import parse_schedule
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
        importer = await r_container.get(Cosplay2Importer)
        await importer.sync_all()
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
