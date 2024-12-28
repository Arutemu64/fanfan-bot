import asyncio
import sys

import uvicorn
from dishka.integrations.faststream import setup_dishka
from faststream.asgi import AsgiFastStream
from prometheus_client import CollectorRegistry, make_asgi_app

from fanfan.adapters.config.parsers import get_config
from fanfan.common.telemetry import setup_telemetry
from fanfan.main.di import create_system_container
from fanfan.presentation.stream.broker import create_broker


def create_app() -> AsgiFastStream:
    config = get_config()

    tracer_provider = setup_telemetry(service_name="faststream", config=config)
    registry = CollectorRegistry()

    broker = create_broker(
        config=config.nats, tracer_provider=tracer_provider, registry=registry
    )

    # Create app
    app = AsgiFastStream(
        broker,
        asgi_routes=[
            ("/metrics", make_asgi_app(registry)),
        ],
    )

    # Setup Dishka
    container = create_system_container()
    setup_dishka(container, app, auto_inject=True)

    return app


def main():
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    uvicorn.run(create_app(), host="0.0.0.0", port=8000)  # noqa: S104


if __name__ == "__main__":
    main()
