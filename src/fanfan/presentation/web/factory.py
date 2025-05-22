import typing
from contextlib import asynccontextmanager

from dishka.integrations.fastapi import setup_dishka
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from fanfan.adapters.config.models import Configuration
from fanfan.common.debug.config import DebugConfig
from fanfan.main.di import create_web_container
from fanfan.presentation.web.admin import setup_admin
from fanfan.presentation.web.admin.auth import admin_auth_router
from fanfan.presentation.web.api import setup_api_router
from fanfan.presentation.web.config import WebConfig
from fanfan.presentation.web.webapp import setup_webapp_router

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


@asynccontextmanager
async def lifespan(app: FastAPI):
    container: AsyncContainer = app.state.dishka_container

    # Setup admin
    config: Configuration = await container.get(Configuration)
    setup_admin(
        app=app, config=config, session_pool=await container.get(async_sessionmaker)
    )

    yield
    await app.state.dishka_container.close()


def create_app(web_config: WebConfig, debug_config: DebugConfig) -> FastAPI:
    # Setup FastAPI app
    app = FastAPI(lifespan=lifespan, debug=debug_config.enabled)

    # Setup DI
    setup_dishka(container=create_web_container(), app=app)

    # Include routers
    app.include_router(setup_webapp_router())
    app.include_router(setup_api_router())
    app.include_router(admin_auth_router)

    # Setup FastAPI middlewares
    app.add_middleware(
        SessionMiddleware,
        secret_key=web_config.secret_key.get_secret_value(),
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app
