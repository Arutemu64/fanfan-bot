from aiogram import Router

from src.bot.filters import RoleFilter
from src.bot.middlewares import ReturnToDialog


def setup_router() -> Router:
    from . import announce_mode, auth, common, org, qr, voting

    auth_router = Router()
    auth_router.include_router(auth.router)
    auth_router.include_router(common.router)

    common_router = Router()
    common_router.message.filter(RoleFilter(["visitor", "helper", "org"]))
    common_router.include_router(voting.router)
    common_router.include_router(qr.router)

    helper_router = Router()
    helper_router.message.filter(RoleFilter(["helper", "org"]))
    helper_router.include_router(announce_mode.router)

    org_router = Router()
    org_router.message.filter(RoleFilter(["org"]))
    org_router.include_router(org.router)

    commands_router = Router()
    commands_router.include_router(auth_router)
    commands_router.include_router(common_router)
    commands_router.include_router(helper_router)
    commands_router.include_router(org_router)
    commands_router.message.middleware(ReturnToDialog())

    return commands_router
