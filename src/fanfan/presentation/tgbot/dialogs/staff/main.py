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
from dishka import AsyncContainer

from fanfan.adapters.auth.utils.token import JwtTokenProcessor
from fanfan.adapters.config.models import Configuration
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.user import UserData
from fanfan.core.services.tickets import TicketsService
from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


async def staff_main_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserData,
    **kwargs,
):
    config: Configuration = await container.get(Configuration)
    tickets_service: TicketsService = await container.get(TicketsService)
    token_processor: JwtTokenProcessor = await container.get(JwtTokenProcessor)

    try:
        tickets_service.ensure_user_can_create_tickets(user)
        can_create_tickets = True
    except AccessDenied:
        can_create_tickets = False

    jwt_token = token_processor.create_access_token(dialog_manager.event.from_user.id)
    return {
        "is_helper": user.role in [UserRole.HELPER, UserRole.ORG],
        "is_org": user.role is UserRole.ORG,
        "can_create_tickets": can_create_tickets,
        "docs_link": config.docs_link,
        "qr_scanner_url": config.web.build_qr_scanner_url() if config.web else None,
        "admin_auth_url": config.web.build_admin_auth_url(jwt_token),
    }


staff_main_window = Window(
    Title(Const(strings.titles.staff_menu)),
    Const(
        "🔨 В этом разделе собраны различные полезные инструменты "
        "для всей команды фестиваля - волонтеров и организаторов. "
        "Набор доступных функций зависит от роли и выданных разрешений."
    ),
    Group(
        SwitchTo(
            state=states.Staff.CREATE_TICKET_PICK_ROLE,
            id="new_ticket",
            text=Const("🎫 Новый билет"),
            when=F["can_create_tickets"],
        ),
        SwitchTo(
            Const("🛍️ Новый магазин"),
            id="new_market",
            state=states.Staff.CREATE_MARKET,
            when=F["is_org"],
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
