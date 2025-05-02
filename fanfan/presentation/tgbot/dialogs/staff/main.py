from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Group,
    Start,
    SwitchTo,
    Url,
)
from aiogram_dialog.widgets.text import Case, Const, Format
from dishka import AsyncContainer

from fanfan.adapters.auth.utils.token import JwtTokenProcessor
from fanfan.adapters.config.models import Configuration
from fanfan.application.settings.get_settings import GetSettings
from fanfan.application.settings.update_settings import (
    UpdateSettings,
)
from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.models.user import UserFull, UserRole
from fanfan.core.services.access import AccessService
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

ID_TOGGLE_VOTING_BUTTON = "id_toggle_voting_button"


async def staff_main_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserFull,
    **kwargs,
):
    config: Configuration = await container.get(Configuration)
    access: AccessService = await container.get(AccessService)
    token_processor: JwtTokenProcessor = await container.get(JwtTokenProcessor)
    get_settings: GetSettings = await container.get(GetSettings)

    try:
        access.ensure_can_create_tickets(user)
        can_create_tickets = True
    except AccessDenied:
        can_create_tickets = False

    settings = await get_settings()
    jwt_token = token_processor.create_access_token(dialog_manager.event.from_user.id)
    return {
        "is_helper": user.role in [UserRole.HELPER, UserRole.ORG],
        "is_org": user.role is UserRole.ORG,
        "can_create_tickets": can_create_tickets,
        "docs_link": config.docs_link,
        "qr_scanner_url": config.web.build_qr_scanner_url() if config.web else None,
        "admin_auth_url": config.web.build_admin_auth_url(jwt_token),
        "voting_enabled": settings.voting_enabled,
    }


async def toggle_voting_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_settings: GetSettings = await container.get(GetSettings)
    update_settings: UpdateSettings = await container.get(UpdateSettings)

    settings = await get_settings()
    await update_settings.toggle_voting(voting_enabled=not settings.voting_enabled)


staff_main_window = Window(
    Title(Const(strings.titles.staff_menu)),
    Group(
        SwitchTo(
            state=states.Staff.CREATE_TICKET_PICK_ROLE,
            id="new_ticket",
            text=Const("🎫 Новый билет"),
            when=F["can_create_tickets"],
        ),
        SwitchTo(
            Const("🛍️ Создать магазин на основе заявки C2"),
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
        Url(
            text=Const("🌐 Орг-панель"),
            url=Format("{admin_auth_url}"),
            when=F["admin_auth_url"] & F["is_org"],
        ),
        Start(
            state=states.UserManager.MANUAL_USER_SEARCH,
            id="user_search",
            text=Const("🔍 Найти пользователя"),
        ),
        Button(
            Case(
                {
                    True: Const("🔴 Выключить голосование"),
                    False: Const("🟢 Включить голосование"),
                },
                selector="voting_enabled",
            ),
            id=ID_TOGGLE_VOTING_BUTTON,
            on_click=toggle_voting_handler,
            when=F["is_org"],
        ),
        Url(
            text=Const(strings.buttons.help_page),
            url=Format("{docs_link}"),
            when=F["docs_link"],
        ),
        width=1,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Staff.MAIN,
    getter=staff_main_getter,
)
