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
from fanfan.application.users.update_user import (
    UpdateUser,
    UpdateUserDTO,
    UpdateUserSettingsDTO,
)
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.page import Pagination
from fanfan.core.models.user import FullUserDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.getters import (
    CURRENT_USER,
    current_user_getter,
)
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    DATA_SELECTED_EVENT_ID,
    current_event_getter,
)
from fanfan.presentation.tgbot.static.templates import subscriptions_list
from fanfan.presentation.tgbot.ui import strings

ID_SUBSCRIPTIONS_SCROLL = "subscriptions_scroll"
ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX = "receive_all_announcements_checkbox"


async def subscriptions_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: FullUserDTO,
    **kwargs,
):
    get_subscriptions_page = await container.get(GetSubscriptionsPage)

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
        dialog_manager.dialog_data[DATA_SELECTED_EVENT_ID] = int(data.replace("/", ""))
        await dialog_manager.switch_to(states.Schedule.event_details)


async def toggle_all_notifications_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_user_by_id = await container.get(GetUserById)
    update_user = await container.get(UpdateUser)

    user: FullUserDTO = manager.middleware_data["user"]
    try:
        await update_user(
            UpdateUserDTO(
                id=user.id,
                settings=UpdateUserSettingsDTO(
                    receive_all_announcements=not user.settings.receive_all_announcements,  # noqa: E501
                ),
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
                True: Const("🔔 Все выступления"),
                False: Const("🔕 Только подписки"),
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
