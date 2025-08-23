import asyncio
import sys

from fanfan.adapters.config.parsers import get_config
from fanfan.adapters.debug.logging import setup_logging
from fanfan.adapters.debug.telemetry import setup_telemetry


def init(service_name: str) -> None:
    config = get_config()

    # Setup logging
    setup_logging(
        level=config.debug.logging_level,
        json_logs=config.debug.json_logs,
    )

    # Setup telemetry
    setup_telemetry(
        service_name=service_name,
        environment=config.env,
        logfire_token=config.debug.logfire_token.get_secret_value()
        if config.debug.logfire_token
        else None,
    )

    # Fix asyncio issues on Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
