import asyncio
import sys

from dishka.integrations.faststream import setup_dishka
from faststream import FastStream

from fanfan.adapters.config.parsers import get_config
from fanfan.adapters.debug.telemetry import setup_telemetry
from fanfan.main.di import create_system_container
from fanfan.presentation.stream.broker import create_broker


def create_app() -> FastStream:
    config = get_config()

    setup_telemetry(
        service_name="stream",
        environment=config.env,
        logfire_token=config.debug.logfire_token.get_secret_value()
        if config.debug.logfire_token
        else None,
    )

    broker = create_broker(config=config.nats)

    # Create app
    app = FastStream(broker)

    # Setup Dishka
    container = create_system_container()
    setup_dishka(container, app)

    return app


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    app = create_app()
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
