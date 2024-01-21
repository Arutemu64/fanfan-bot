from contextlib import suppress

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input.text import ManagedTextInput, TextInput
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

from fanfan.application.dto.subscription import CreateSubscriptionDTO, SubscriptionDTO
from fanfan.application.dto.user import FullUserDTO, UpdateUserDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.exceptions.event import NoCurrentEvent
from fanfan.application.exceptions.subscriptions import (
    SubscriptionNotFound,
)
from fanfan.application.services import ServicesHolder
from fanfan.presentation.tgbot.dialogs import (
    states,
)
from fanfan.presentation.tgbot.dialogs.menus.schedule.common import (
    ScheduleWindow,
    set_search_query_handler,
)
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.static.templates import subscriptions_list
from fanfan.presentation.tgbot.ui import strings

ID_SUBSCRIPTIONS_SCROLL = "subscriptions_scroll"
ID_EVENT_INPUT = "event_input"
ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX = "receive_all_announcements_checkbox"

DATA_CURRENT_SUBSCRIPTION_DTO = "current_subscription_dto"
DATA_SELECTED_EVENT_TITLE = "selected_event_title"


async def subscriptions_getter(
    dialog_manager: DialogManager, user: FullUserDTO, services: ServicesHolder, **kwargs
):
    page = await services.subscriptions.get_subscriptions_page(
        user_id=user.id,
        page=await dialog_manager.find(ID_SUBSCRIPTIONS_SCROLL).get_page(),
        subscriptions_per_page=user.items_per_page,
    )
    try:
        current_event_position = (
            await services.events.get_current_event()
        ).real_position
    except NoCurrentEvent:
        current_event_position = 0
    return {
        "receive_all_announcements": user.receive_all_announcements,
        "pages": page.total,
        "subscriptions": page.items,
        "current_event_position": current_event_position,
    }


async def create_subscription_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    services: ServicesHolder = dialog_manager.middleware_data["services"]
    try:
        subscription = await services.subscriptions.create_subscription(
            CreateSubscriptionDTO(
                user_id=dialog_manager.event.from_user.id,
                event_id=data,
            )
        )
        dialog_manager.dialog_data[
            DATA_CURRENT_SUBSCRIPTION_DTO
        ] = subscription.model_dump()
        dialog_manager.dialog_data[DATA_SELECTED_EVENT_TITLE] = subscription.event.title
        await dialog_manager.switch_to(states.SCHEDULE.SUBSCRIPTIONS_SET_COUNTER)
    except ServiceError as e:
        await message.reply(e.message)
        return


async def update_subscription_counter_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    services: ServicesHolder = dialog_manager.middleware_data["services"]
    subscription = SubscriptionDTO.model_validate(
        dialog_manager.dialog_data[DATA_CURRENT_SUBSCRIPTION_DTO]
    )
    try:
        await services.subscriptions.update_subscription_counter(
            subscription_id=subscription.id,
            counter=data,
        )
    except ServiceError as e:
        await message.reply(e.message)
        return
    await message.reply(
        f"✅ Подписка на выступление "
        f"<b>{subscription.event.title}</b>"
        f" успешно оформлена!"
    )
    await dialog_manager.switch_to(states.SCHEDULE.SUBSCRIPTIONS_MAIN)


async def cancel_subscription_creation_handler(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    services: ServicesHolder = manager.middleware_data["services"]
    subscription = SubscriptionDTO.model_validate(
        manager.dialog_data[DATA_CURRENT_SUBSCRIPTION_DTO]
    )
    with suppress(SubscriptionNotFound):
        await services.subscriptions.delete_subscription(subscription.id)
    await manager.switch_to(states.SCHEDULE.SUBSCRIPTIONS_EVENT_SELECTOR)


async def remove_subscription_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    services: ServicesHolder = dialog_manager.middleware_data["services"]
    try:
        await services.subscriptions.delete_subscription_by_event(
            user_id=dialog_manager.event.from_user.id, event_id=data
        )
    except ServiceError as e:
        await message.reply(e.message)
        return

    await message.reply("🗑️ Подписка удалена!")


async def toggle_all_notifications_handler(
    callback: CallbackQuery, button: Button, manager: DialogManager
):
    user: FullUserDTO = manager.middleware_data["user"]
    services: ServicesHolder = manager.middleware_data["services"]
    try:
        manager.middleware_data["user"] = await services.users.update_user(
            UpdateUserDTO(
                id=user.id, receive_all_announcements=not user.receive_all_announcements
            )
        )
    except ServiceError as e:
        await callback.answer(e.message)


set_counter_window = Window(
    Format(
        """🔢 За сколько выступлений до начала """
        """<b>{dialog_data[selected_event_title]}</b> начать оповещать Вас?"""
    ),
    TextInput(
        id="counter_input",
        type_factory=int,
        on_success=update_subscription_counter_handler,
    ),
    Button(
        text=Const(strings.buttons.back),
        id="back",
        on_click=cancel_subscription_creation_handler,
    ),
    state=states.SCHEDULE.SUBSCRIPTIONS_SET_COUNTER,
)

select_event_window = ScheduleWindow(
    state=states.SCHEDULE.SUBSCRIPTIONS_EVENT_SELECTOR,
    header=Title(
        Const("➕ Пришлите номер выступления, на которое хотите подписаться:"),
        upper=False,
    ),
    after_paginator=SwitchTo(
        text=Const(strings.buttons.back),
        state=states.SCHEDULE.SUBSCRIPTIONS_MAIN,
        id="back",
    ),
    text_input=TextInput(
        id=ID_EVENT_INPUT,
        type_factory=int,
        on_success=create_subscription_handler,
        on_error=set_search_query_handler,
    ),
)

subscriptions_main_window = Window(
    Title(Const(strings.titles.notifications)),
    Jinja(subscriptions_list),
    Const(
        "🗑️ <i>Чтобы отписаться, пришлите номер выступления</i>",
        when=F["subscriptions"],
    ),
    TextInput(
        id="REMOVE_SUBSCRIPTION_INPUT",
        type_factory=int,
        on_success=remove_subscription_handler,
    ),
    SwitchTo(
        text=Const("➕ Подписаться на выступление"),
        state=states.SCHEDULE.SUBSCRIPTIONS_EVENT_SELECTOR,
        id="subscribe",
    ),
    Button(
        Case(
            {
                True: Const("🔕 Получать только свои уведомления"),
                False: Const("🔔 Получать все уведомления"),
            },
            selector=F["receive_all_announcements"],
        ),
        id=ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX,
        on_click=toggle_all_notifications_handler,
    ),
    StubScroll(ID_SUBSCRIPTIONS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_SUBSCRIPTIONS_SCROLL, text=Format(text="{current_page1}/{pages}")
        ),
        NextPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_SUBSCRIPTIONS_SCROLL, text=Const("⏭️")),
        when=F["pages"] > 1,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        id="close_subscriptions",
        state=states.SCHEDULE.MAIN,
    ),
    getter=subscriptions_getter,
    state=states.SCHEDULE.SUBSCRIPTIONS_MAIN,
)
