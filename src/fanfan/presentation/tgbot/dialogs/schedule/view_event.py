from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, SwitchTo
from aiogram_dialog.widgets.text import Case, Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.schedule.get_schedule_event_by_id import (
    GetScheduleEventById,
    GetScheduleEventByIdDTO,
)
from fanfan.application.schedule.management.set_current_event import (
    SetCurrentScheduleEvent,
    SetCurrentScheduleEventDTO,
)
from fanfan.application.schedule.management.skip_event import (
    SkipScheduleEvent,
    SkipScheduleEventDTO,
)
from fanfan.application.schedule.subscriptions.delete_subscription import (
    DeleteSubscription,
    DeleteSubscriptionDTO,
)
from fanfan.core.constants.permissions import Permissions
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.schedule.data import ScheduleDialogData
from fanfan.presentation.tgbot.dialogs.schedule.getters import (
    current_event_getter,
    helpers_schedule_getter,
)
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import selected_event_info


@inject
async def event_details_getter(
    dialog_manager: DialogManager,
    dialog_data_adapter: DialogDataAdapter,
    get_event_by_id: FromDishka[GetScheduleEventById],
    **kwargs,
):
    dialog_data = dialog_data_adapter.load(ScheduleDialogData)
    event = await get_event_by_id(
        GetScheduleEventByIdDTO(event_id=dialog_data.event_id)
    )
    return {
        "event_id": event.id,
        "event_public_id": event.public_id,
        "event_title": event.title,
        "event_is_current": event.is_current,
        "event_is_skipped": event.is_skipped,
        "event_cumulative_duration": event.cumulative_duration,
        "event_duration": event.duration,
        "event_queue": event.queue,
        "nomination_title": event.nomination_title,
        "block_title": event.block_title,
        "user_is_subscribed": bool(event.subscription),
    }


@inject
async def set_as_current(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    set_current_event: FromDishka[SetCurrentScheduleEvent],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(ScheduleDialogData)
    result = await set_current_event(
        SetCurrentScheduleEventDTO(event_id=dialog_data.event_id)
    )
    await callback.message.answer(
        f"✅ Выступление <b>{result.current_event.title}</b> отмечено как текущее\n"
    )
    manager.show_mode = ShowMode.DELETE_AND_SEND


@inject
async def unset_current(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    set_current_event: FromDishka[SetCurrentScheduleEvent],
) -> None:
    await set_current_event(SetCurrentScheduleEventDTO(event_id=None))
    await callback.answer("⛔ С выступления снята отметка Текущее")


@inject
async def skip_event_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    skip_event: FromDishka[SkipScheduleEvent],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(ScheduleDialogData)
    result = await skip_event(SkipScheduleEventDTO(event_id=dialog_data.event_id))
    if result.event.is_skipped:
        text = f"🙈 Выступление <b>{result.event.title}</b> пропущено"
    else:
        text = f"🙉 Выступление <b>{result.event.title}</b> возвращено"
    await callback.message.answer(text)
    manager.show_mode = ShowMode.DELETE_AND_SEND


@inject
async def unsubscribe_button_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    get_event_by_id: FromDishka[GetScheduleEventById],
    delete_subscription: FromDishka[DeleteSubscription],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(ScheduleDialogData)
    event = await get_event_by_id(
        GetScheduleEventByIdDTO(event_id=dialog_data.event_id)
    )
    if event.subscription:
        await delete_subscription(
            DeleteSubscriptionDTO(subscription_id=event.subscription.id)
        )
    await callback.answer("🗑️ Подписка удалена!")


selected_event_window = Window(
    Jinja("<b>🎭 ВЫСТУПЛЕНИЕ №{{ '%03d' % event_public_id }}</b>"),
    Jinja(" └ <i>🗂️ {{ block_title }}</i>", when="block_title"),
    Const(" "),
    Jinja(selected_event_info),
    SwitchTo(
        text=Const("🔔 Подписаться"),
        id="subscribe",
        state=states.Schedule.ADD_SUBSCRIPTION,
        when=~F["user_is_subscribed"],
    ),
    Button(
        text=Const("🔕 Отписаться"),
        id="unsubscribe",
        on_click=unsubscribe_button_handler,
        when=F["user_is_subscribed"],
    ),
    Group(
        Button(
            text=Const("🎬 Отметить текущим"),
            id="set_as_current",
            on_click=set_as_current,
            when=~F["event_is_current"] & ~F["event_is_skipped"],
        ),
        Button(
            text=Const("⛔ Снять отметку Текущее"),
            id="unset_current",
            on_click=unset_current,
            when=F["event_is_current"],
        ),
        SwitchTo(
            text=Const("🔀 Переместить"),
            id="move_event",
            state=states.Schedule.MOVE_EVENT,
        ),
        Button(
            text=Case(
                texts={False: Const("🙈 Пропустить"), True: Const("🙉 Вернуть")},
                selector=F["event_is_skipped"],
            ),
            id="skip_event",
            on_click=skip_event_handler,
            when=~F["event_is_current"],
        ),
        when=F[Permissions.CAN_MANAGE_SCHEDULE],
    ),
    Cancel(Const(strings.buttons.back), id="back"),
    getter=[event_details_getter, current_event_getter, helpers_schedule_getter],
    state=states.Schedule.EVENT_DETAILS,
)
