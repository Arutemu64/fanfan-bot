import asyncio
import logging
import platform
from contextlib import asynccontextmanager

import sentry_sdk
import uvicorn
from aiogram.fsm.storage.memory import SimpleEventIsolation
from arq import create_pool
from fastapi import FastAPI
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.redis import RedisIntegration
from sentry_sdk.integrations.sqlalchemy import SqlalchemyIntegration
from starlette.middleware.sessions import SessionMiddleware

from fanfan.application.services.settings import SettingsService
from fanfan.common.enums import BotMode
from fanfan.common.factory import (
    create_bot,
)
from fanfan.config import conf
from fanfan.infrastructure.db.main import create_async_engine, create_session_pool
from fanfan.infrastructure.db.uow import UnitOfWork
from fanfan.infrastructure.redis import create_redis_client, create_redis_storage
from fanfan.infrastructure.scheduler import create_worker
from fanfan.presentation.sqladmin.admin import setup_admin
from fanfan.presentation.tgbot.dispatcher import create_dispatcher
from fanfan.presentation.tgbot.utils.webapp import webapp_router
from fanfan.presentation.tgbot.utils.webhook import webhook_router


@asynccontextmanager
async def lifespan(app: FastAPI):
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

    bot = create_bot()
    engine = create_async_engine(conf.db.build_connection_str())
    session_pool = create_session_pool(engine)

    async with session_pool() as session:
        uow = UnitOfWork(session)
        await SettingsService(uow).setup_initial_settings()

    redis = create_redis_client()
    await redis.ping()

    dp, dialog_bg_factory = create_dispatcher(
        storage=create_redis_storage(redis=redis),
        event_isolation=SimpleEventIsolation(),
    )

    dp["session_pool"] = session_pool

    # TODO Do I really need these?
    # TODO Bot and session pool are safe to re-create anyway
    app.state.dp = dp
    app.state.bot = bot
    app.state.session_pool = session_pool
    app.state.dialog_bg_factory = dialog_bg_factory

    setup_admin(app, session_pool)

    if conf.web.mode == BotMode.WEBHOOK:
        webhook_url = conf.web.build_webhook_url()
        app.include_router(webhook_router)
        app.include_router(webapp_router)
        if (await bot.get_webhook_info()).url != webhook_url:
            await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
        logging.info(f"Running in webhook mode at {(await bot.get_webhook_info()).url}")
    elif conf.web.mode == BotMode.POLLING:
        await bot.delete_webhook(drop_pending_updates=True)
        asyncio.create_task(dp.start_polling(bot))
        logging.info("Running in polling mode")
    worker = create_worker(await create_pool(conf.redis.get_pool_settings()))
    asyncio.create_task(worker.async_run())
    yield
    logging.info("Stopping schedule worker...")
    await worker.close()
    logging.info("Closing bot session...")
    await bot.session.close()
    logging.info("Disposing db engine...")
    await engine.dispose()
    logging.info("Bot stopped!")


app = FastAPI(lifespan=lifespan, debug=conf.debug)
app.add_middleware(SessionMiddleware, secret_key=conf.web.secret_key.get_secret_value())

if __name__ == "__main__":
    logging.basicConfig(level=conf.logging_level)
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    uvicorn.run(
        host=conf.web.host,
        port=conf.web.port,
        app="fanfan.presentation.tgbot.__main__:app",
    )
