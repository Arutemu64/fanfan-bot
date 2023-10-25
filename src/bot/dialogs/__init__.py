from aiogram import Router

from src.bot.filters import RoleFilter
from src.bot.structures import UserRole


def setup_router() -> Router:
    from src.bot.dialogs import (
        helper,
        main,
        org,
        registration,
        schedule,
        settings,
        user_manager,
        voting,
    )

    unregistered_router = Router()
    unregistered_router.include_router(registration.dialog)

    visitor_router = Router()
    visitor_filter = RoleFilter([UserRole.VISITOR, UserRole.HELPER, UserRole.ORG])
    visitor_router.callback_query.filter(visitor_filter)
    visitor_router.message.filter(visitor_filter)
    visitor_router.include_router(main.dialog)
    visitor_router.include_router(schedule.dialog)
    visitor_router.include_router(voting.dialog)
    visitor_router.include_router(settings.dialog)

    helper_router = Router()
    helper_filter = RoleFilter([UserRole.HELPER, UserRole.ORG])
    helper_router.callback_query.filter(helper_filter)
    helper_router.message.filter(helper_filter)
    helper_router.include_router(helper.dialog)
    helper_router.include_router(user_manager.dialog)

    org_router = Router()
    org_filter = RoleFilter([UserRole.ORG])
    org_router.callback_query.filter(org_filter)
    org_router.message.filter(org_filter)
    org_router.include_router(org.dialog)

    dialog_router = Router()
    dialog_router.include_router(unregistered_router)
    dialog_router.include_router(visitor_router)
    dialog_router.include_router(helper_router)
    dialog_router.include_router(org_router)

    return dialog_router
