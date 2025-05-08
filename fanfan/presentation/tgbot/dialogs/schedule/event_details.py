from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Jinja
from dishka import AsyncContainer

from fanfan.application.schedule.get_event_for_user import GetEventForUser
from fanfan.application.schedule.management.set_current_event import SetCurrentEvent
from fanfan.application.schedule.management.skip_event import SkipEvent
from fanfan.application.schedule.subscriptions.delete_subscription_by_event import (
    DeleteSubscriptionByEvent,
)
from fanfan.core.models.schedule_event import ScheduleEventId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.schedule.common import (
    CAN_EDIT_SCHEDULE,
    DATA_SELECTED_EVENT_ID,
    can_edit_schedule_getter,
    current_event_getter,
)
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import selected_event_info

SELECTED_EVENT = "selected_event"


async def show_event_details(manager: DialogManager, event_id: ScheduleEventId) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    get_event_by_id: GetEventForUser = await container.get(GetEventForUser)
    await get_event_by_id(event_id)
    await manager.start(
        state=states.Schedule.EVENT_DETAILS, data={DATA_SELECTED_EVENT_ID: event_id}
    )


async def selected_event_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    get_event_by_id: GetEventForUser = await container.get(GetEventForUser)
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
        text = f"🙈 Выступление <b>{data.event.title}</b> пропущено"
    else:
        text = f"🙉 Выступление <b>{data.event.title}</b> возвращено"
    await callback.message.answer(text)
    manager.show_mode = ShowMode.DELETE_AND_SEND


async def unsubscribe_button_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    delete_subscription: DeleteSubscriptionByEvent = await container.get(
        DeleteSubscriptionByEvent
    )

    await delete_subscription(
        ScheduleEventId(manager.start_data[DATA_SELECTED_EVENT_ID])
    )
    await callback.answer("🗑️ Подписка удалена!")


selected_event_window = Window(
    Title(Jinja("🎭 Выступление №{{ selected_event.id }}")),
    Jinja(selected_event_info),
    SwitchTo(
        text=Const("🔔 Подписаться"),
        id="subscribe",
        state=states.Schedule.ADD_SUBSCRIPTION,
        when=~F[SELECTED_EVENT].subscription,
    ),
    Button(
        text=Const("🔕 Отписаться"),
        id="unsubscribe",
        on_click=unsubscribe_button_handler,
        when=F[SELECTED_EVENT].subscription,
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
            state=states.Schedule.MOVE_EVENT,
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
        when=F[CAN_EDIT_SCHEDULE],
    ),
    Cancel(Const(strings.buttons.back), id="back"),
    getter=[selected_event_getter, current_event_getter, can_edit_schedule_getter],
    state=states.Schedule.EVENT_DETAILS,
)
