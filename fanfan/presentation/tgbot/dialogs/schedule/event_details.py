from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, SwitchTo
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
from fanfan.core.models.event import EventId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.predicates import is_helper
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    DATA_SELECTED_EVENT_ID,
    current_event_getter,
)
from fanfan.presentation.tgbot.keyboards.buttons import show_mailing_info_button
from fanfan.presentation.tgbot.static.templates import selected_event_info
from fanfan.presentation.tgbot.ui import strings

SELECTED_EVENT = "selected_event"


async def show_event_details(manager: DialogManager, event_id: EventId) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_event_by_id: GetEventById = await container.get(GetEventById)
    await get_event_by_id(event_id)
    await manager.start(
        state=states.Schedule.event_details, data={DATA_SELECTED_EVENT_ID: event_id}
    )


async def selected_event_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    get_event_by_id: GetEventById = await container.get(GetEventById)
    return {
        SELECTED_EVENT: await get_event_by_id(
            dialog_manager.start_data[DATA_SELECTED_EVENT_ID],
        ),
    }


async def set_as_current(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    set_current_event: SetCurrentEvent = await container.get(SetCurrentEvent)

    data = await set_current_event(manager.start_data[DATA_SELECTED_EVENT_ID])
    await callback.message.answer(
        f"✅ Выступление <b>{data.current_event.title}</b> отмечено как текущее\n"
        f"Уникальный ID рассылки: <code>{data.mailing_id}</code>",
        reply_markup=InlineKeyboardBuilder(
            [[show_mailing_info_button(data.mailing_id)]]
        ).as_markup(),
    )
    manager.show_mode = ShowMode.DELETE_AND_SEND


async def unset_current(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    set_current_event: SetCurrentEvent = await container.get(SetCurrentEvent)

    await set_current_event(None)
    await callback.answer("⛔ С выступления снята отметка Текущее")


async def skip_event_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    skip_event: SkipEvent = await container.get(SkipEvent)

    data = await skip_event(manager.start_data[DATA_SELECTED_EVENT_ID])
    if data.event.is_skipped:
        text = (
            f"🙈 Выступление <b>{data.event.title}</b> пропущено\n"
            f"Уникальный ID рассылки: <code>{data.mailing_id}</code>"
        )
    else:
        text = (
            f"🙉 Выступление <b>{data.event.title}</b> возвращено\n"
            f"Уникальный ID рассылки: <code>{data.mailing_id}</code>"
        )
    await callback.message.answer(
        text,
        reply_markup=InlineKeyboardBuilder(
            [[show_mailing_info_button(data.mailing_id)]]
        ).as_markup(),
    )
    manager.show_mode = ShowMode.DELETE_AND_SEND


async def unsubscribe_button_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_subscription_by_event: GetSubscriptionByEvent = await container.get(
        GetSubscriptionByEvent
    )
    delete_subscription: DeleteSubscription = await container.get(DeleteSubscription)

    try:
        subscription = await get_subscription_by_event(
            manager.start_data[DATA_SELECTED_EVENT_ID]
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
            when=~F[SELECTED_EVENT].is_current & ~F[SELECTED_EVENT].is_skipped,
        ),
        Button(
            text=Const("⛔ Снять отметку Текущее"),
            id="unset_current",
            on_click=unset_current,
            when=F[SELECTED_EVENT].is_current,
        ),
        SwitchTo(
            text=Const("🔀 Переместить"),
            id="move_event",
            state=states.Schedule.move_event,
        ),
        Button(
            text=Case(
                texts={False: Const("🙈 Пропустить"), True: Const("🙉 Вернуть")},
                selector=F[SELECTED_EVENT].is_skipped,
            ),
            id="skip_event",
            on_click=skip_event_handler,
            when=~F[SELECTED_EVENT].is_current,
        ),
        when=is_helper,
    ),
    Cancel(Const(strings.buttons.back), id="back"),
    getter=[selected_event_getter, current_event_getter],
    state=states.Schedule.event_details,
)
