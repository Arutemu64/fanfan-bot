import asyncio
import logging
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from aiogram.fsm.storage.redis import RedisEventIsolation
from fastapi import FastAPI
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from starlette.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from taskiq.api import run_receiver_task

from fanfan.application.services.settings import SettingsService
from fanfan.common.enums import BotMode
from fanfan.common.factory import (
    create_bot,
)
from fanfan.config import conf
from fanfan.infrastructure.db.main import create_async_engine, create_session_pool
from fanfan.infrastructure.db.uow import UnitOfWork
from fanfan.infrastructure.redis import create_redis_client, create_redis_storage
from fanfan.infrastructure.scheduler import broker
from fanfan.presentation.sqladmin.admin import setup_admin
from fanfan.presentation.tgbot.dispatcher import create_dispatcher
from fanfan.presentation.tgbot.utils.webapp import webapp_router
from fanfan.presentation.tgbot.utils.webhook import webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Setup Sentry logging
    if conf.sentry.enabled:
        sentry_sdk.init(
            dsn=conf.sentry.dsn,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
            environment=conf.sentry.env,
            integrations=[
                AsyncioIntegration(),
                SqlalchemyIntegration(),
                RedisIntegration(),
            ],
        )

    # Setup dependencies
    bot = create_bot()
    engine = create_async_engine(conf.db.build_connection_str())
    session_pool = create_session_pool(engine)
    redis = create_redis_client()
    await redis.ping()
    dp, dialog_bg_factory = create_dispatcher(
        storage=create_redis_storage(redis=redis),
        event_isolation=RedisEventIsolation(redis),
    )

    dp["session_pool"] = session_pool
    app.state.dp = dp
    app.state.bot = bot
    app.state.session_pool = session_pool
    app.state.dialog_bg_factory = dialog_bg_factory

    # Run scheduler
    broker.state.dialog_bg_factory = dialog_bg_factory
    worker_task = asyncio.create_task(run_receiver_task(broker, run_startup=True))

    # Setup default settings
    async with session_pool() as session:
        uow = UnitOfWork(session)
        await SettingsService(uow).setup_initial_settings()

    # Setup admin
    setup_admin(app, session_pool)

    # Run bot
    bot_task = None
    if conf.web.mode == BotMode.WEBHOOK:
        webhook_url = conf.web.build_webhook_url()
        app.include_router(webhook_router)
        app.include_router(webapp_router)
        if (await bot.get_webhook_info()).url != webhook_url:
            await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        logging.info(f"Running in webhook mode at {(await bot.get_webhook_info()).url}")
    elif conf.web.mode == BotMode.POLLING:
        await bot.delete_webhook(drop_pending_updates=True)
        bot_task = asyncio.create_task(dp.start_polling(bot))
        logging.info("Running in polling mode")
    yield
    logging.info("Stopping scheduler worker...")
    worker_task.cancel()
    await broker.shutdown()
    logging.info("Closing bot session...")
    await bot.session.close()
    if bot_task:
        bot_task.cancel()
    logging.info("Disposing db engine...")
    await engine.dispose()
    logging.info("Bot stopped!")


app = FastAPI(lifespan=lifespan, debug=conf.debug)
app.add_middleware(SessionMiddleware, secret_key=conf.web.secret_key.get_secret_value())
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    logging.basicConfig(level=conf.logging_level)
    uvicorn.run(
        host=conf.web.host,
        port=conf.web.port,
        app=app,
    )
