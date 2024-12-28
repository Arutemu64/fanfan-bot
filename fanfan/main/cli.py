import asyncio
import sys

import click
from dishka.integrations.click import CONTAINER_NAME

from fanfan.adapters.config.parsers import get_config
from fanfan.common.logging import setup_logging
from fanfan.common.telemetry import setup_telemetry
from fanfan.main.di import create_system_container
from fanfan.presentation.cli.commands.participants import (
    import_from_c2_command,
    parse_schedule_command,
)
from fanfan.presentation.cli.commands.tickets import (
    import_orders_command,
    parse_tickets_command,
)


@click.group()
@click.pass_context
def cli(context: click.Context):
    # No setup_dishka in there because it doesn't support async containers
    context.meta[CONTAINER_NAME] = create_system_container()


def main():
    config = get_config()
    setup_logging(
        level=config.debug.logging_level,
        json_logs=config.debug.json_logs,
    )
    setup_telemetry(
        service_name="cli",
        config=config,
    )

    # Setup commands
    cli.add_command(parse_schedule_command)
    cli.add_command(import_from_c2_command)
    cli.add_command(import_orders_command)
    cli.add_command(parse_tickets_command)

    # Fix running on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run
    cli()


if __name__ == "__main__":
    main()
