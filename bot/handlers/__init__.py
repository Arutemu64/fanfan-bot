from aiogram import Router

from bot import middlewares
from bot.handlers import cb_factories


def setup_routers() -> Router:
    from . import activities, announce, auth, common, helper, org, qr, schedule, voting

    router = Router()
    router.include_router(activities.router)
    router.include_router(announce.router)
    router.include_router(auth.router)
    router.include_router(common.router)
    router.include_router(helper.router)
    router.include_router(org.router)
    router.include_router(qr.router)
    router.include_router(schedule.router)
    router.include_router(voting.router)

    return router
