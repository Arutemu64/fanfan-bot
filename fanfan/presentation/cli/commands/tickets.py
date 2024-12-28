import logging
from typing import TYPE_CHECKING, BinaryIO

import click
from dishka.integrations.click import CONTAINER_NAME
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.adapters.utils.parsers.parse_tickets import parse_tickets
from fanfan.application.utils.import_orders import ImportOrders
from fanfan.presentation.cli.commands.common import async_command

if TYPE_CHECKING:
    from dishka import AsyncContainer

logger = logging.getLogger(__name__)


@click.command(name="import_orders")
@click.pass_context
@async_command
async def import_orders_command(context: click.Context):
    container: AsyncContainer = context.meta[CONTAINER_NAME]
    async with container() as r_container:
        interactor: ImportOrders = await r_container.get(ImportOrders)
        result = await interactor()
        logger.info("Importing from C2 done!", extra={"result": result})


@click.command(name="parse_tickets")
@click.argument("tickets", type=click.File("rb"))
@click.pass_context
@async_command
async def parse_tickets_command(context: click.Context, tickets: BinaryIO):
    container: AsyncContainer = context.meta[CONTAINER_NAME]
    async with container() as r_container:
        session: AsyncSession = await r_container.get(AsyncSession)
        await parse_tickets(file=tickets, session=session)
