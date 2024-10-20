import asyncio
import sys
from contextlib import asynccontextmanager, suppress
from typing import TYPE_CHECKING

import sentry_sdk
import uvicorn
from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from fanfan.adapters.config_reader import get_config
from fanfan.main.di import create_web_container
from fanfan.presentation.web.admin import setup_admin
from fanfan.presentation.web.webapp import setup_webapp_router

if TYPE_CHECKING:
    from dishka import AsyncContainer


@asynccontextmanager
async def lifespan(app: FastAPI):
    container: AsyncContainer = app.state.dishka_container

    # Setup admin
    setup_admin(app, await container.get(async_sessionmaker))

    yield
    await app.state.dishka_container.close()


def create_app() -> FastAPI:
    config = get_config()

    # Setup Sentry logging
    if config.debug.sentry_enabled:
        sentry_sdk.init(
            dsn=config.debug.sentry_dsn,
            environment=config.debug.sentry_env,
        )

    # Setup FastAPI app
    app = FastAPI(lifespan=lifespan, debug=config.debug.enabled)

    # Setup DI
    setup_dishka(container=create_web_container(), app=app)

    # Include routers
    app.include_router(setup_webapp_router())

    # Setup FastAPI middlewares
    app.add_middleware(
        SessionMiddleware,
        secret_key=config.web.secret_key.get_secret_value(),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    config = get_config()
    with suppress(KeyboardInterrupt):
        uvicorn.run(
            create_app(),
            host=config.web.host,
            port=config.web.port,
            root_path="/web",
            log_level=config.debug.logging_level,
        )
