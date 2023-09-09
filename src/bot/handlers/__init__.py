from aiogram import Router

from src.bot.filters import RoleFilter
from src.bot.structures import UserRole


def setup_router() -> Router:
    from . import callbacks, start

    common_router = Router()
    common_router.message.filter(
        RoleFilter([UserRole.VISITOR, UserRole.HELPER, UserRole.ORG])
    )
    common_router.include_router(callbacks.router)

    helper_router = Router()
    helper_router.message.filter(RoleFilter([UserRole.HELPER, UserRole.ORG]))

    org_router = Router()
    org_router.message.filter(RoleFilter([UserRole.ORG]))

    handlers_router = Router()
    handlers_router.include_router(start.router)
    handlers_router.include_router(common_router)
    handlers_router.include_router(helper_router)
    handlers_router.include_router(org_router)

    return handlers_router
