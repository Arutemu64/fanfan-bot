from dishka.integrations.faststream import setup_dishka
from faststream import FastStream
from faststream.nats import NatsBroker

from fanfan.infrastructure.config_reader import get_config
from fanfan.main.di import create_scheduler_container
from fanfan.presentation.faststream.routes import setup_router


def create_app() -> FastStream:
    config = get_config()

    # Create broker, attach routers
    broker = NatsBroker(config.nats.build_connection_str())
    broker.include_router(setup_router())

    # Create app
    app = FastStream(broker)

    # Setup Dishka
    container = create_scheduler_container()
    setup_dishka(container, app, auto_inject=True)

    return app
