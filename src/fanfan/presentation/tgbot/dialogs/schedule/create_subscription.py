import typing

from aiogram.types import Message
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.schedule.subscriptions.create_subscription import (
    CreateSubscription,
    CreateSubscriptionDTO,
)
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.schedule.common import DATA_SELECTED_EVENT_ID
from fanfan.presentation.tgbot.static import strings

if typing.TYPE_CHECKING:
    from dishka import AsyncContainer


async def set_counter_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    create_subscription: CreateSubscription = await container.get(CreateSubscription)

    subscription = await create_subscription(
        CreateSubscriptionDTO(
            event_id=dialog_manager.start_data[DATA_SELECTED_EVENT_ID], counter=data
        )
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
