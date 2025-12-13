from aiogram import F
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Group,
    Start,
    SwitchTo,
    Url,
)
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.adapters.auth.utils.token import JwtTokenProcessor
from fanfan.adapters.config.models import EnvConfig
from fanfan.core.constants.permissions import Permissions
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


@inject
async def staff_main_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    config: FromDishka[EnvConfig],
    token_processor: FromDishka[JwtTokenProcessor],
    **kwargs,
):
    can_create_tickets = current_user.check_permission(Permissions.CAN_CREATE_TICKETS)
    can_view_participants = current_user.check_permission(
        Permissions.CAN_VIEW_PARTICIPANTS
    )
    jwt_token = token_processor.create_access_token(current_user.id)
    return {
        "docs_link": config.docs_link,
        "qr_scanner_url": config.web.build_qr_scanner_url() if config.web else None,
        "admin_auth_url": config.web.build_admin_auth_url(jwt_token),
        # Permissions
        "is_helper": current_user.role in [UserRole.HELPER, UserRole.ORG],
        "is_org": current_user.role is UserRole.ORG,
        "can_create_tickets": can_create_tickets,
        "can_view_participants": can_view_participants,
    }


staff_main_window = Window(
    Title(Const(strings.titles.staff_menu)),
    Const(
        "🔨 В этом разделе собраны различные полезные инструменты "
        "для всей команды фестиваля - волонтеров и организаторов. "
        "Набор доступных функций зависит от роли и выданных разрешений."
    ),
    Group(
        Start(
            text=Const(strings.titles.participants),
            state=states.Participants.LIST_PARTICIPANTS,
            id="participants",
            when=F["can_view_participants"],
        ),
        SwitchTo(
            state=states.Staff.CREATE_TICKET_PICK_ROLE,
            id="new_ticket",
            text=Const("🎫 Новый билет"),
            when=F["can_create_tickets"],
        ),
        Start(
            state=states.Mailing.MAIN,
            id="new_notification",
            text=Const("✉️ Рассылки"),
            when=F["is_org"],
        ),
        Start(
            state=states.UserManager.MANUAL_USER_SEARCH,
            id="user_search",
            text=Const("🔍 Найти пользователя"),
        ),
        Url(
            text=Const("🌐 Орг-панель"),
            url=Format("{admin_auth_url}"),
            when=F["admin_auth_url"] & F["is_org"],
        ),
        Url(
            text=Const(strings.buttons.help_page),
            url=Format("{docs_link}"),
            when=F["docs_link"],
        ),
        width=2,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Staff.MAIN,
    getter=[staff_main_getter],
)
