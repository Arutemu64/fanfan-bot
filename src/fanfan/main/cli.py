import asyncio
import sys

import click
from dishka.integrations.click import CONTAINER_NAME

from fanfan.adapters.config.parsers import get_config
from fanfan.adapters.debug.logging import setup_logging
from fanfan.adapters.debug.telemetry import setup_telemetry
from fanfan.main.di import create_system_container
from fanfan.presentation.cli.commands.program import (
    parse_schedule_command,
    sync_cosplay2_command,
)
from fanfan.presentation.cli.commands.tickets import (
    parse_tickets_command,
    sync_tcloud_command,
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
        environment=config.env,
        logfire_token=config.debug.logfire_token.get_secret_value()
        if config.debug.logfire_token
        else None,
    )

    # Setup commands
    cli.add_command(parse_schedule_command)
    cli.add_command(sync_cosplay2_command)
    cli.add_command(sync_tcloud_command)
    cli.add_command(parse_tickets_command)

    # Fix running on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    # Run
    cli()


if __name__ == "__main__":
    main()
