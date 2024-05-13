from aiogram import Router

from fanfan.common.enums import UserRole
from fanfan.presentation.tgbot.utils.filters import RoleFilter


def setup_router() -> Router:
    from fanfan.presentation.tgbot.dialogs import (
        achievements,
        activities,
        deliveries,
        feedback,
        helper,
        main,
        org,
        schedule,
        settings,
        user_manager,
        voting,
    )
    from fanfan.presentation.tgbot.dialogs.schedule import event_details

    common_router = Router(name="common_dialog_router")
    common_router.include_routers(
        main.dialog,
        schedule.dialog,
        event_details.dialog,
        achievements.dialog,
        voting.dialog,
        settings.dialog,
        feedback.dialog,
        activities.dialog,
    )

    helper_router = Router(name="helper_dialog_router")
    helper_router.callback_query.filter(RoleFilter([UserRole.HELPER, UserRole.ORG]))
    helper_router.message.filter(RoleFilter([UserRole.HELPER, UserRole.ORG]))
    helper_router.include_routers(helper.dialog, user_manager.dialog)

    org_router = Router(name="org_dialog_router")
    org_router.callback_query.filter(RoleFilter([UserRole.ORG]))
    org_router.include_routers(org.dialog, deliveries.dialog)

    dialog_router = Router(name="dialog_router")
    dialog_router.include_routers(common_router, helper_router, org_router)

    return dialog_router
