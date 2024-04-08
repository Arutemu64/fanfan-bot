import asyncio
import logging
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from aiogram import Bot, Dispatcher
from dishka import AsyncContainer, make_async_container
from dishka.integrations.fastapi import setup_dishka as setup_dishka_fastapi
from dishka.integrations.taskiq import setup_dishka as setup_dishka_taskiq
from fastapi import FastAPI
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from taskiq.api import run_receiver_task

from fanfan.application.services.settings import SettingsService
from fanfan.common.enums import BotMode
from fanfan.config import get_config
from fanfan.infrastructure.db.uow import UnitOfWork
from fanfan.infrastructure.scheduler import broker
from fanfan.presentation.admin import setup_admin
from fanfan.presentation.tgbot.web.webapp import webapp_router
from fanfan.presentation.tgbot.web.webhook import webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    app_container: AsyncContainer = app.state.dishka_container
    config = get_config()

    # Setup Sentry logging
    if config.debug.sentry_enabled:
        sentry_sdk.init(
            dsn=config.debug.sentry_dsn,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=config.debug.sentry_env,
            integrations=[
                AsyncioIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
        )

    # Run scheduler
    setup_dishka_taskiq(app_container, broker)
    worker_task = asyncio.create_task(run_receiver_task(broker, run_startup=True))

    async with app_container() as request_container:
        uow = await request_container.get(UnitOfWork)
        await SettingsService(uow).setup_initial_settings()

    # Setup admin
    setup_admin(app, await app_container.get(async_sessionmaker))

    # Setup and run bot
    bot = await app_container.get(Bot)
    bot_task = None
    match config.web.mode:
        case BotMode.WEBHOOK:
            webhook_url = config.web.build_webhook_url()
            app.include_router(webhook_router)
            app.include_router(webapp_router)
            if (await bot.get_webhook_info()).url != webhook_url:
                await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
            logging.info(
                f"Running in webhook mode at {(await bot.get_webhook_info()).url}",
            )
        case BotMode.POLLING:
            dp = await app_container.get(Dispatcher)
            await bot.delete_webhook(drop_pending_updates=True)
            bot_task = asyncio.create_task(dp.start_polling(bot))
            logging.info("Running in polling mode")
    yield
    logging.info("Stopping scheduler worker...")
    worker_task.cancel()
    await broker.shutdown()
    logging.info("Stopping bot...")
    if bot_task:
        bot_task.cancel()
    logging.info("Disposing container...")
    await app_container.close()
    logging.info("Bot stopped!")


def create_app() -> FastAPI:
    config = get_config()

    # Setup FastAPI app
    app = FastAPI(lifespan=lifespan, debug=config.debug.enabled)

    # Setup DI
    from fanfan.infrastructure.di import get_app_providers

    app_container = make_async_container(*get_app_providers())
    setup_dishka_fastapi(app_container, app)

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
    config = get_config()
    logging.basicConfig(level=config.debug.logging_level)
    try:
        uvicorn.run(
            host=config.web.host,
            port=config.web.port,
            app=create_app(),
        )
    except KeyboardInterrupt:
        pass
