import asyncio
import sys
from contextlib import suppress

import uvicorn

from fanfan.adapters.config.parsers import get_config
from fanfan.common.debug.logging import setup_logging
from fanfan.common.debug.telemetry import setup_telemetry
from fanfan.presentation.web.factory import create_app


def main():
    config = get_config()
    setup_logging(
        level=config.debug.logging_level,
        json_logs=config.debug.json_logs,
    )
    setup_telemetry(
        service_name="web",
        environment=config.env,
        logfire_token=config.debug.logfire_token.get_secret_value()
        if config.debug.logfire_token
        else None,
    )
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with suppress(KeyboardInterrupt):
        uvicorn.run(
            create_app(web_config=config.web_config, debug_config=config.debug_config),
            host=config.web.host,
            port=config.web.port,
            root_path=config.web.path,
            proxy_headers=True,
            forwarded_allow_ips=["*"],
            log_level=config.debug.logging_level,
            log_config=None,
        )


if __name__ == "__main__":
    main()
