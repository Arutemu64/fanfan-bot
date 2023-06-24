# системные импорты
import sys
import logging
import asyncio

# всё что касается ТГ-бота
from aiogram import Bot, Dispatcher, F
from aiogram.enums.parse_mode import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

# для работы с БД
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

# роутеры и мидлвари
from bot.handlers import callbacks, commands, states
from bot.middlewares import DbSessionMiddleware, RoleMiddleware

# конфиг
from bot.config import conf


async def main():
    # cоздаем движок и sessionmaker для работы с БД
    engine = create_async_engine(url=conf.db.build_connection_str(), echo=True)
    sessionmaker = async_sessionmaker(engine, expire_on_commit=False)

    # создаём диспетчера
    dp = Dispatcher(storage=MemoryStorage())

    # подключаем к диспетчеру две мидлвари (работа с БД и проверка роли) и фильтр на личные чаты
    dp.update.middleware(DbSessionMiddleware(session_pool=sessionmaker))
    dp.message.filter(F.chat.type == "private")

    callbacks.router.callback_query.middleware(RoleMiddleware())
    commands.router.message.middleware(RoleMiddleware())

    # подлючаем к диспетчеру роутеры коллбэков, команд и состояний
    dp.include_router(callbacks.router)
    dp.include_router(commands.router)
    dp.include_router(states.router)

    # создаём бота, не реагируем на старые сообщения
    bot = Bot(token=conf.bot.token, parse_mode=ParseMode.HTML)
    await bot.delete_webhook(drop_pending_updates=True)

    # запускаем пулинг бота
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=conf.logging_level)
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print('Bot stopped!')
