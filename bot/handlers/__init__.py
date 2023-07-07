from aiogram import Router

from bot import middlewares
from bot.handlers import cb_factories


def setup_routers() -> Router:
    from . import announce, auth, common, navigation, org, qr, schedule_viewer, voting

    router = Router()
    router.include_router(announce.router)
    router.include_router(auth.router)
    router.include_router(common.router)
    router.include_router(helper.router)
    router.include_router(org.router)
    router.include_router(qr.router)
    router.include_router(schedule.router)
    router.include_router(voting.router)

    router.message.middleware(middlewares.RoleMiddleware())
    router.callback_query.middleware(middlewares.RoleMiddleware())

    return router
