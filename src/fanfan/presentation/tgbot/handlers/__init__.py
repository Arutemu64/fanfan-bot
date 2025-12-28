from aiogram import Router

from . import callbacks, commands
from .callbacks import callbacks_router
from .commands import commands_router


def setup_handlers_router() -> Router:
    handlers_router = Router(name="handlers_router")
    handlers_router.include_router(commands_router)
    handlers_router.include_router(callbacks_router)
    return handlers_router
