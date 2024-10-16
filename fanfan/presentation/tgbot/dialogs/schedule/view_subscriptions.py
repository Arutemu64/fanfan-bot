from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja
from dishka import AsyncContainer

from fanfan.application.subscriptions.get_subscriptions_page import GetSubscriptionsPage
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.application.users.update_user_settings import (
    UpdateUserSettings,
    UpdateUserSettingsDTO,
)
from fanfan.core.exceptions.base import AppException
from fanfan.core.exceptions.events import EventNotFound
from fanfan.core.models.event import EventId
from fanfan.core.models.page import Pagination
from fanfan.core.models.user import FullUserModel
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import (
    CURRENT_USER,
    current_user_getter,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    current_event_getter,
)
from fanfan.presentation.tgbot.dialogs.schedule.event_details import show_event_details
from fanfan.presentation.tgbot.static.templates import subscriptions_list
from fanfan.presentation.tgbot.ui import strings

ID_SUBSCRIPTIONS_SCROLL = "subscriptions_scroll"
ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX = "receive_all_announcements_checkbox"


async def subscriptions_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: FullUserModel,
    **kwargs,
):
    get_subscriptions_page: GetSubscriptionsPage = await container.get(
        GetSubscriptionsPage
    )

    page = await get_subscriptions_page(
        pagination=Pagination(
            limit=user.settings.items_per_page,
            offset=await dialog_manager.find(ID_SUBSCRIPTIONS_SCROLL).get_page()
            * user.settings.items_per_page,
        )
    )
    return {
        "subscriptions": page.items,
        "pages": page.total // user.settings.items_per_page
        + bool(page.total % user.settings.items_per_page),
    }


async def subscriptions_text_input_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    if "/" in data and data.replace("/", "").isnumeric():
        event_id = EventId(int(data.replace("/", "")))
        try:
            await show_event_details(dialog_manager, event_id)
        except EventNotFound as e:
            await message.answer(e.message)
            return


async def toggle_all_notifications_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_user_by_id: GetUserById = await container.get(GetUserById)
    update_user_settings: UpdateUserSettings = await container.get(UpdateUserSettings)

    user: FullUserModel = manager.middleware_data["user"]
    try:
        await update_user_settings(
            UpdateUserSettingsDTO(
                user_id=user.id,
                receive_all_announcements=not user.settings.receive_all_announcements,
            ),
        )
        manager.middleware_data["user"] = await get_user_by_id(user.id)
    except AppException as e:
        await callback.answer(e.message)


subscriptions_main_window = Window(
    Title(Const(strings.titles.notifications)),
    Jinja(subscriptions_list),
    Const(
        "➕ <i>Чтобы подписаться, нажми на номер выступления в расписании</i>",
        when=~F["subscriptions"],
    ),
    TextInput(
        id="subscriptions_text_input",
        type_factory=str,
        on_success=subscriptions_text_input_handler,
    ),
    Button(
        Case(
            {
                True: Const("🔔 Получать все уведомления: ✅"),
                False: Const("🔔 Получать все уведомления: ❌"),
            },
            selector=F[CURRENT_USER].settings.receive_all_announcements,
        ),
        id=ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX,
        on_click=toggle_all_notifications_handler,
    ),
    StubScroll(ID_SUBSCRIPTIONS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_SUBSCRIPTIONS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("⏭️")),
        when=F["pages"] > 1,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        id="back",
        state=states.Schedule.main,
    ),
    getter=[subscriptions_getter, current_event_getter, current_user_getter],
    state=states.Schedule.subscriptions,
)
