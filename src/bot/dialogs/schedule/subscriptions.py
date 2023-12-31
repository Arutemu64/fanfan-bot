from aiogram import F
from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.dialog import ChatEvent
from aiogram_dialog.widgets.input.text import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Checkbox,
    CurrentPage,
    FirstPage,
    LastPage,
    ManagedCheckbox,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja

from src.bot.dialogs import states
from src.bot.dialogs.schedule.common import (
    ID_SCHEDULE_SCROLL,
    ScheduleWindow,
    set_search_query,
)
from src.bot.dialogs.templates import subscriptions_list
from src.bot.dialogs.widgets import Title
from src.bot.ui import strings
from src.db import Database
from src.db.models import DBUser

ID_SUBSCRIPTIONS_SCROLL = "subscriptions_scroll"
ID_EVENT_INPUT = "event_input"
ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX = "receive_all_announcements_checkbox"


async def subscriptions_getter(
    dialog_manager: DialogManager, db: Database, current_user: DBUser, **kwargs
):
    page = await db.subscription.paginate(
        page=await dialog_manager.find(ID_SUBSCRIPTIONS_SCROLL).get_page(),
        subscriptions_per_page=current_user.items_per_page,
        user=current_user,
    )
    current_event = await db.event.get_current()
    checkbox: ManagedCheckbox = dialog_manager.find(
        ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX
    )
    await checkbox.set_checked(current_user.receive_all_announcements)
    return {
        "pages": page.total,
        "subscriptions": page.items,
        "current_event_position": current_event.real_position if current_event else 0,
    }


async def select_event(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]
    user = dialog_manager.middleware_data["current_user"]
    event = await db.event.get(data)

    if not event:
        await message.reply("⚠️ Выступление не найдено!")
        return
    if event.skip:
        await message.reply("⚠️ На это выступление нельзя подписаться!")
        return
    if await db.subscription.get_subscription_for_user(user, event):
        await message.reply("⚠️ Вы уже подписаны на это выступление!")
        return

    dialog_manager.dialog_data["selected_event_title"] = event.title
    await dialog_manager.switch_to(states.SCHEDULE.SUBSCRIPTIONS_SET_COUNTER)


async def setup_subscription(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]
    user: DBUser = dialog_manager.middleware_data["current_user"]
    event = await db.event.get(int(dialog_manager.find(ID_EVENT_INPUT).get_value()))

    subscription = await db.subscription.new(user, event, data)
    await db.session.commit()
    await message.reply(
        f"✅ Подписка на выступление "
        f"<b>{subscription.event.title}</b>"
        f" успешно оформлена!"
    )
    await dialog_manager.switch_to(states.SCHEDULE.SUBSCRIPTIONS_MAIN)


async def remove_subscription(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]
    user: DBUser = dialog_manager.middleware_data["current_user"]
    event = await db.event.get(data)

    subscription = await db.subscription.get_subscription_for_user(user, event)
    if subscription:
        await db.session.delete(subscription)
        await db.session.commit()
        await message.reply("🗑️ Подписка удалена!")
    else:
        await message.reply("⚠️ Подписка не найдена!")
        return


async def toggle_all_notifications(
    event: ChatEvent, checkbox: ManagedCheckbox, manager: DialogManager
):
    db: Database = manager.middleware_data["db"]
    user: DBUser = manager.middleware_data["current_user"]
    user.receive_all_announcements = checkbox.is_checked()
    await db.session.commit()


set_counter_window = Window(
    Format(
        "🔢 За сколько выступлений до начала "
        "<b>{dialog_data[selected_event_title]}</b> начать оповещать Вас?"
    ),
    TextInput(id="counter_input", type_factory=int, on_success=setup_subscription),
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.SCHEDULE.SUBSCRIPTIONS_EVENT_SELECTOR,
        id="back",
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
        id="event_selector_window_input",
        type_factory=int,
        on_success=select_event,
        on_error=set_search_query,
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
        on_success=remove_subscription,
    ),
    SwitchTo(
        text=Const("➕ Подписаться на выступление"),
        state=states.SCHEDULE.SUBSCRIPTIONS_EVENT_SELECTOR,
        id="subscribe",
    ),
    Checkbox(
        Const("🔕 Получать только свои уведомления"),
        Const("🔔 Получать все уведомления"),
        id=ID_RECEIVE_ALL_ANNOUNCEMENTS_CHECKBOX,
        on_state_changed=toggle_all_notifications,
    ),
    StubScroll(ID_SUBSCRIPTIONS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_SCHEDULE_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_SCHEDULE_SCROLL, text=Format(text="{current_page1}/{pages}")
        ),
        NextPage(scroll=ID_SCHEDULE_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_SCHEDULE_SCROLL, text=Const("⏭️")),
        when=F["pages"] != 1,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        id="close_subscriptions",
        state=states.SCHEDULE.MAIN,
    ),
    getter=subscriptions_getter,
    state=states.SCHEDULE.SUBSCRIPTIONS_MAIN,
)
