from aiogram import Router

from bot import middlewares


def setup_routers() -> Router:
    from . import announce, auth, common, navigation, orgs, qr, schedule_viewer, voting

    router = Router()
    router.include_router(announce.router)
    router.include_router(auth.router)
    router.include_router(common.router)
    router.include_router(navigation.router)
    router.include_router(orgs.router)
    router.include_router(qr.router)
    router.include_router(schedule_viewer.router)
    router.include_router(voting.router)

    router.message.middleware(middlewares.RoleMiddleware())
    router.callback_query.middleware(middlewares.RoleMiddleware())

    return router
