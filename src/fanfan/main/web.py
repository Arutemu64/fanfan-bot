from contextlib import suppress

import logfire
import uvicorn

from fanfan.adapters.config.parsers import get_config
from fanfan.main.common import init
from fanfan.presentation.web.factory import create_app


def main():
    init(service_name="web")

    config = get_config()
    app = create_app(web_config=config.web, debug_config=config.debug)
    logfire.instrument_fastapi(app)
    with suppress(KeyboardInterrupt):
        uvicorn.run(
            app,
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
