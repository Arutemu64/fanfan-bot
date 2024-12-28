import logging
from typing import TYPE_CHECKING, BinaryIO

import click
from dishka.integrations.click import CONTAINER_NAME
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.utils.parsers.parse_schedule import parse_schedule
from fanfan.application.utils.import_from_c2 import ImportFromC2
from fanfan.presentation.cli.commands.common import async_command

if TYPE_CHECKING:
    from dishka import AsyncContainer

logger = logging.getLogger(__name__)


@click.command(name="parse_schedule")
@click.argument("schedule", type=click.File("rb"))
@click.pass_context
@async_command
async def parse_schedule_command(context: click.Context, schedule: BinaryIO):
    container: AsyncContainer = context.meta[CONTAINER_NAME]
    async with container() as r_container:
        session: AsyncSession = await r_container.get(AsyncSession)
        await parse_schedule(file=schedule, session=session)


@click.command(name="import_from_c2")
@click.pass_context
@async_command
async def import_from_c2_command(context: click.Context):
    container: AsyncContainer = context.meta[CONTAINER_NAME]
    async with container() as r_container:
        interactor: ImportFromC2 = await r_container.get(ImportFromC2)
        result = await interactor()
        logger.info("Importing from C2 done!", extra={"result": result})
