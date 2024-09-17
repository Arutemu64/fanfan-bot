from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Button, Group, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Jinja
from dishka import AsyncContainer

from fanfan.application.events.get_event_by_id import GetEventById
from fanfan.application.schedule_mgmt.set_current_event import SetCurrentEvent
from fanfan.application.schedule_mgmt.skip_event import SkipEvent
from fanfan.application.subscriptions.delete_subscription import DeleteSubscription
from fanfan.application.subscriptions.get_subscription_by_event import (
    GetSubscriptionByEvent,
)
from fanfan.core.exceptions.base import AppException
from fanfan.core.utils.pluralize import NOTIFICATIONS_PLURALS, pluralize
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.predicates import is_helper
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    DATA_SELECTED_EVENT_ID,
    current_event_getter,
)
from fanfan.presentation.tgbot.keyboards.buttons import get_delete_mailing_button
from fanfan.presentation.tgbot.static.templates import selected_event_info
from fanfan.presentation.tgbot.ui import strings

SELECTED_EVENT = "selected_event"


async def selected_event_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    get_event_by_id = await container.get(GetEventById)
    return {
        SELECTED_EVENT: await get_event_by_id(
            dialog_manager.dialog_data[DATA_SELECTED_EVENT_ID],
        ),
    }


async def set_as_current(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    set_current_event = await container.get(SetCurrentEvent)

    try:
        data = await set_current_event(manager.dialog_data[DATA_SELECTED_EVENT_ID])
        await callback.message.answer(
            f"✅ Выступление <b>{data.current_event.title}</b> отмечено как текущее\n"
            f"Будет отправлено {data.mailing_info.count} "
            f"{pluralize(data.mailing_info.count, NOTIFICATIONS_PLURALS)}\n"
            f"Уникальный ID рассылки: <code>{data.mailing_info.mailing_id}</code>",
            reply_markup=InlineKeyboardBuilder(
                [
                    [
                        get_delete_mailing_button(data.mailing_info.mailing_id),
                    ],
                ],
            ).as_markup()
            if data.mailing_info.count > 0
            else None,
        )
        manager.show_mode = ShowMode.DELETE_AND_SEND
    except AppException as e:
        await callback.answer(e.message)
        return


async def unset_current(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    set_current_event = await container.get(SetCurrentEvent)

    try:
        await set_current_event(None)
        await callback.answer("⛔ С выступления снята отметка Текущее")
    except AppException as e:
        await callback.answer(e.message)
        return


async def skip_event_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    skip_event = await container.get(SkipEvent)

    try:
        data = await skip_event(manager.dialog_data[DATA_SELECTED_EVENT_ID])
        if data.event.skip:
            text = (
                f"🙈 Выступление <b>{data.event.title}</b> пропущено\n"
                f"Будет отправлено {data.mailing_info.count} "
                f"{pluralize(data.mailing_info.count, NOTIFICATIONS_PLURALS)}\n"
                f"Уникальный ID рассылки: <code>{data.mailing_info.mailing_id}</code>"
            )
        else:
            text = (
                f"🙉 Выступление <b>{data.event.title}</b> возвращено\n"
                f"Будет отправлено {data.mailing_info.count} "
                f"{pluralize(data.mailing_info.count, NOTIFICATIONS_PLURALS)}\n"
                f"Уникальный ID рассылки: <code>{data.mailing_info.mailing_id}</code>"
            )
        await callback.message.answer(
            text,
            reply_markup=InlineKeyboardBuilder(
                [
                    [
                        get_delete_mailing_button(data.mailing_info.mailing_id),
                    ],
                ],
            ).as_markup()
            if data.mailing_info.count > 0
            else None,
        )
        manager.show_mode = ShowMode.DELETE_AND_SEND
    except AppException as e:
        await callback.answer(e.message)
        return


async def unsubscribe_button_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_subscription_by_event = await container.get(GetSubscriptionByEvent)
    delete_subscription = await container.get(DeleteSubscription)

    try:
        subscription = await get_subscription_by_event(
            manager.dialog_data[DATA_SELECTED_EVENT_ID]
        )
        await delete_subscription(subscription.id)
        await callback.answer("🗑️ Подписка удалена!")
    except AppException as e:
        await callback.answer(e.message, show_alert=True)
        manager.show_mode = ShowMode.DELETE_AND_SEND
        return


selected_event_window = Window(
    Title(Const("🎭 Выступление")),
    Jinja(selected_event_info),
    SwitchTo(
        text=Const("🔔 Подписаться"),
        id="subscribe",
        state=states.Schedule.add_subscription,
        when=~F[SELECTED_EVENT].user_subscription,
    ),
    Button(
        text=Const("🔕 Отписаться"),
        id="unsubscribe",
        on_click=unsubscribe_button_handler,
        when=F[SELECTED_EVENT].user_subscription,
    ),
    Group(
        Button(
            text=Const("🎬 Отметить текущим"),
            id="set_as_current",
            on_click=set_as_current,
            when=~F[SELECTED_EVENT].current & ~F[SELECTED_EVENT].skip,
        ),
        Button(
            text=Const("⛔ Снять отметку Текущее"),
            id="unset_current",
            on_click=unset_current,
            when=F[SELECTED_EVENT].current,
        ),
        SwitchTo(
            text=Const("🔀 Переместить"),
            id="move_event",
            state=states.Schedule.move_event,
        ),
        Button(
            text=Case(
                texts={False: Const("🙈 Пропустить"), True: Const("🙉 Вернуть")},
                selector=F["selected_event"].skip,
            ),
            id="skip_event",
            on_click=skip_event_handler,
            when=~F["selected_event"].current,
        ),
        when=is_helper,
    ),
    SwitchTo(Const(strings.buttons.back), state=states.Schedule.main, id="back"),
    getter=[selected_event_getter, current_event_getter],
    state=states.Schedule.event_details,
)
