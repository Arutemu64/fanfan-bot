import asyncio

from dishka.integrations.faststream import setup_dishka
from faststream import FastStream

from fanfan.adapters.config.parsers import get_config
from fanfan.main.common import init
from fanfan.main.di import create_system_container
from fanfan.presentation.stream.broker import create_broker


def create_app() -> FastStream:
    config = get_config()
    broker = create_broker(config=config.nats)
    app = FastStream(broker)
    container = create_system_container()
    setup_dishka(container, app)

    return app


def main():
    init(service_name="stream")
    app = create_app()
    asyncio.run(app.run())


if __name__ == "__main__":
    main()
