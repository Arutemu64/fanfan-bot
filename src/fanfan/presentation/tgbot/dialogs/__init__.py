from aiogram import Router

from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot.dialogs import (
    achievements,
    activities,
    link_ticket,
    mailing,
    main_menu,
    marketplace,
    participants,
    qr,
    quest,
    schedule,
    settings,
    staff,
    user_manager,
    voting,
)
from fanfan.presentation.tgbot.filters import RoleFilter


def setup_router() -> Router:
    common_router = Router(name="common_dialog_router")
    common_router.include_routers(
        main_menu.dialog,
        link_ticket.dialog,
        schedule.dialog,
        achievements.dialog,
        voting.dialog,
        settings.dialog,
        activities.dialog,
        quest.dialog,
        marketplace.dialog,
        qr.dialog,
        participants.dialog,
    )

    helper_router = Router(name="helper_dialog_router")
    helper_router.callback_query.filter(RoleFilter(UserRole.HELPER, UserRole.ORG))
    helper_router.message.filter(RoleFilter(UserRole.HELPER, UserRole.ORG))
    helper_router.include_routers(
        user_manager.dialog,
        mailing.dialog,
        staff.dialog,
    )

    org_router = Router(name="org_dialog_router")
    org_router.callback_query.filter(RoleFilter(UserRole.ORG))

    dialog_router = Router(name="dialog_router")
    dialog_router.include_routers(common_router, helper_router, org_router)

    return dialog_router
