from aiogram import Router

from src.bot.filters import RoleFilter
from src.bot.structures import UserRole


def setup_router() -> Router:
    from . import callbacks, qr, start

    common_router = Router()
    common_router.message.filter(
        RoleFilter([UserRole.VISITOR, UserRole.HELPER, UserRole.ORG])
    )
    common_router.include_router(callbacks.router)
    common_router.include_router(qr.router)

    helper_router = Router()
    helper_router.message.filter(RoleFilter([UserRole.HELPER, UserRole.ORG]))

    org_router = Router()
    org_router.message.filter(RoleFilter([UserRole.ORG]))

    commands_router = Router()
    commands_router.include_router(start.router)
    commands_router.include_router(common_router)
    commands_router.include_router(helper_router)
    commands_router.include_router(org_router)

    return commands_router
