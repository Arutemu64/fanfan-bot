import asyncio
import contextlib
import logging
import sys

import sentry_sdk
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.base import BaseEventIsolation
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram_dialog import setup_dialogs
from aiogram_dialog.context.media_storage import MediaIdStorage
from aiohttp import web
from dishka.integrations.aiogram import setup_dishka
from sqlalchemy.ext.asyncio import AsyncSession

from fanfan.common.config import get_config
from fanfan.core.enums import BotMode
from fanfan.core.utils.settings import setup_initial_settings
from fanfan.infrastructure.di import create_bot_container
from fanfan.presentation.tgbot import dialogs, handlers
from fanfan.presentation.tgbot.handlers.errors import register_error_handlers
from fanfan.presentation.tgbot.middlewares import LoadDataMiddleware

logger = logging.getLogger(__name__)


async def on_startup(bot: Bot) -> None:
    config = get_config()
    match config.bot.mode:
        case BotMode.WEBHOOK:
            logger.info(
                "Running in webhook mode at %s",
                (await bot.get_webhook_info()).url,
            )
        case BotMode.POLLING:
            logger.info("Running in polling mode")


async def main() -> None:
    config = get_config()

    # Setup Sentry logging
    if config.debug.sentry_enabled:
        sentry_sdk.init(
            dsn=config.debug.sentry_dsn,
            environment=config.debug.sentry_env,
        )

    # Get dependencies ready
    container = create_bot_container()
    bot = await container.get(Bot)
    dp: Dispatcher = await container.get(Dispatcher)

    # Setup DI
    setup_dishka(container, dp)

    # Setup handlers
    dp.include_router(handlers.setup_router())  # Handlers must be above dialogs
    register_error_handlers(dp)

    # Setup middlewares
    dp.message.outer_middleware(LoadDataMiddleware())
    dp.callback_query.outer_middleware(LoadDataMiddleware())
    dp.inline_query.outer_middleware(LoadDataMiddleware())
    dp.errors.outer_middleware(LoadDataMiddleware())

    # Setup dialogs
    dp.include_router(dialogs.setup_router())
    setup_dialogs(
        dp,
        media_id_storage=MediaIdStorage(),
        events_isolation=await container.get(BaseEventIsolation),
    )

    # Register startup hook
    dp.startup.register(on_startup)

    # Setup initial settings
    async with container() as container:
        session = await container.get(AsyncSession)
        await setup_initial_settings(session)

    # Run bot
    try:
        match config.bot.mode:
            case BotMode.WEBHOOK:
                app = web.Application()
                webhook_requests_handler = SimpleRequestHandler(
                    dispatcher=dp,
                    bot=bot,
                )
                webhook_requests_handler.register(app, path="/webhook")
                setup_application(app, dp, bot=bot)
                webhook_url = config.web.build_webhook_url()
                if (await bot.get_webhook_info()).url != webhook_url:
                    await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
                await web._run_app(  # noqa: SLF001
                    app,
                    host=config.bot.webhook_host,
                    port=config.bot.webhook_port,
                )
            case BotMode.POLLING:
                await bot.delete_webhook(drop_pending_updates=True)
                await dp.start_polling(bot)
    finally:
        await container.close()


if __name__ == "__main__":
    config = get_config()
    logging.basicConfig(level=config.debug.logging_level)
    if sys.platform == "win32":  # aiodns
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(main())
