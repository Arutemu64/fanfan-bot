from aiogram import Router

from . import callbacks, commands, inline_query


def setup_router() -> Router:
    common_router = Router()
    common_router.include_router(commands.router)
    common_router.include_router(callbacks.router)
    common_router.include_router(inline_query.router)

    helper_router = Router()

    org_router = Router()

    handlers_router = Router()
    handlers_router.include_router(common_router)
    handlers_router.include_router(helper_router)
    handlers_router.include_router(org_router)

    return handlers_router
