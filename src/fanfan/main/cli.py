import click
from dishka.integrations.click import CONTAINER_NAME

from fanfan.main.common import init
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
    init(service_name="cli")

    cli.add_command(parse_schedule_command)
    cli.add_command(sync_cosplay2_command)
    cli.add_command(sync_tcloud_command)
    cli.add_command(parse_tickets_command)

    cli()


if __name__ == "__main__":
    main()
