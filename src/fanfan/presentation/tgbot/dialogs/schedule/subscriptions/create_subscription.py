from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.schedule.subscriptions.create_subscription import (
    CreateSubscription,
    CreateSubscriptionDTO,
)
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.schedule.data import ScheduleDialogData
from fanfan.presentation.tgbot.static import strings


@inject
async def set_counter_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
    create_subscription: FromDishka[CreateSubscription],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(ScheduleDialogData)
    subscription = await create_subscription(
        CreateSubscriptionDTO(event_id=dialog_data.event_id, counter=data)
    )
    await message.reply(
        f"✅ Подписка на выступление "
        f"<b>{subscription.event.title}</b> "
        f"успешно оформлена!",
    )
    await dialog_manager.switch_to(
        states.Schedule.EVENT_DETAILS,
        show_mode=ShowMode.DELETE_AND_SEND,
    )


set_subscription_counter_window = Window(
    Format(
        "🔢 За сколько выступлений до начала начать присылать уведомления?",
    ),
    TextInput(
        id="counter_input",
        type_factory=int,
        on_success=set_counter_handler,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        id="back",
        state=states.Schedule.EVENT_DETAILS,
    ),
    state=states.Schedule.ADD_SUBSCRIPTION,
)
