from aiogram import Router

from src.bot.filters import RoleFilter
from src.bot.middlewares import ReturnToDialog
from src.bot.structures import Role


def setup_router() -> Router:
    from . import callbacks, org, qr, start

    common_router = Router()
    common_router.message.filter(RoleFilter([Role.VISITOR, Role.HELPER, Role.ORG]))
    common_router.message.middleware(ReturnToDialog())
    common_router.include_router(callbacks.router)
    common_router.include_router(qr.router)

    helper_router = Router()
    helper_router.message.filter(RoleFilter([Role.HELPER, Role.ORG]))
    helper_router.message.middleware(ReturnToDialog())

    org_router = Router()
    org_router.message.filter(RoleFilter([Role.ORG]))
    org_router.message.middleware(ReturnToDialog())
    org_router.include_router(org.router)

    commands_router = Router()
    commands_router.include_router(start.router)
    commands_router.include_router(common_router)
    commands_router.include_router(helper_router)
    commands_router.include_router(org_router)
    # commands_router.message.middleware(ReturnToDialog())

    return commands_router
