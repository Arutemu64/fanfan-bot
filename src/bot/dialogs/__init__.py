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
        voting,
    )

    common_router = Router()
    common_router.include_router(registration.dialog)
    common_router.include_router(main.dialog)
    common_router.include_router(schedule.dialog)
    common_router.include_router(voting.dialog)
    common_router.include_router(settings.dialog)

    helper_router = Router()
    helper_router.include_router(helper.dialog)
    helper_router.callback_query.filter(RoleFilter([UserRole.HELPER, UserRole.ORG]))

    org_router = Router()
    org_router.callback_query.filter(RoleFilter([UserRole.ORG]))
    org_router.include_router(org.dialog)

    dialog_router = Router()
    dialog_router.include_router(common_router)
    dialog_router.include_router(helper_router)
    dialog_router.include_router(org_router)

    return dialog_router
