import asyncio
import contextlib
import logging

from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from aiohttp.web_runner import AppRunner, TCPSite

from fanfan.adapters.config.models import Configuration
from fanfan.adapters.config.parsers import get_config
from fanfan.main.common import init
from fanfan.main.di import create_bot_container
from fanfan.presentation.tgbot.config import BotMode

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


async def run_webhook(bot: Bot, dp: Dispatcher, config: Configuration) -> None:
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path="/webhook")
    setup_application(app, dp, bot=bot)
    webhook_url = config.bot.webhook.build_webhook_url()
    if (await bot.get_webhook_info()).url != webhook_url:
        await bot.set_webhook(url=webhook_url, drop_pending_updates=True)
    runner = AppRunner(app)
    await runner.setup()
    site = TCPSite(runner, host=config.bot.webhook.host, port=config.bot.webhook.port)
    await site.start()
    await asyncio.Event().wait()


async def run() -> None:
    # Get dependencies ready
    container = create_bot_container()
    bot: Bot = await container.get(Bot)
    dp: Dispatcher = await container.get(Dispatcher)
    config: Configuration = await container.get(Configuration)

    # Register startup hook
    dp.startup.register(on_startup)

    # Run bot
    try:
        match config.bot.mode:
            case BotMode.WEBHOOK:
                await run_webhook(bot, dp, config)
            case BotMode.POLLING:
                await bot.delete_webhook(drop_pending_updates=True)
                await dp.start_polling(bot)
    finally:
        await container.close()


def main():
    init(service_name="bot")
    with contextlib.suppress(KeyboardInterrupt):
        asyncio.run(run())


if __name__ == "__main__":
    main()
