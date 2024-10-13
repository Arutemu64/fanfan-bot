from aiogram import Router

from fanfan.core.enums import UserRole
from fanfan.presentation.tgbot.dialogs import (
    achievements,
    activities,
    feedback,
    helper,
    mailing,
    main_menu,
    org,
    quest,
    schedule,
    settings,
    user_manager,
    voting,
)
from fanfan.presentation.tgbot.filters import RoleFilter


def setup_router() -> Router:
    common_router = Router(name="common_dialog_router")
    common_router.include_routers(
        main_menu.dialog,
        schedule.dialog,
        achievements.dialog,
        voting.dialog,
        settings.dialog,
        feedback.dialog,
        activities.dialog,
        quest.dialog,
    )

    helper_router = Router(name="helper_dialog_router")
    helper_router.callback_query.filter(RoleFilter(UserRole.HELPER, UserRole.ORG))
    helper_router.message.filter(RoleFilter(UserRole.HELPER, UserRole.ORG))
    helper_router.include_routers(helper.dialog, user_manager.dialog, mailing.dialog)

    org_router = Router(name="org_dialog_router")
    org_router.callback_query.filter(RoleFilter(UserRole.ORG))
    org_router.include_routers(org.dialog)

    dialog_router = Router(name="dialog_router")
    dialog_router.include_routers(common_router, helper_router, org_router)

    return dialog_router
