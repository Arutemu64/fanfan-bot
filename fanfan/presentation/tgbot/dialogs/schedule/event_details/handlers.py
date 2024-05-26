from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram_dialog import DialogManager, ShowMode
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from fanfan.application.dto.subscription import CreateSubscriptionDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.holder import AppHolder
from fanfan.common.utils import NOTIFICATIONS_PLURALS, pluralize
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.buttons import get_delete_delivery_button
from fanfan.presentation.tgbot.dialogs.schedule import show_event_page
from fanfan.presentation.tgbot.dialogs.schedule.common import set_search_query


async def set_as_current(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    try:
        event, delivery_info = await app.schedule_mgmt.set_current_event(
            manager.start_data
        )
        await callback.message.answer(
            f"✅ Выступление <b>{event.title}</b> отмечено как текущее\n"
            f"Будет отправлено {delivery_info.count} "
            f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}\n"
            f"Уникальный ID рассылки: <code>{delivery_info.delivery_id}</code>",
            reply_markup=InlineKeyboardBuilder(
                [
                    [
                        get_delete_delivery_button(delivery_info.delivery_id),
                    ]
                ]
            ).as_markup()
            if delivery_info.count > 0
            else None,
        )
        manager.show_mode = ShowMode.DELETE_AND_SEND
    except ServiceError as e:
        await callback.answer(e.message)
        return


async def skip_event(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    try:
        event, delivery_info = await app.schedule_mgmt.skip_event(manager.start_data)
        if event.skip:
            text = (
                f"🙈 Выступление <b>{event.title}</b> пропущено\n"
                f"Будет отправлено {delivery_info.count} "
                f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}\n"
                f"Уникальный ID рассылки: <code>{delivery_info.delivery_id}</code>"
            )
        else:
            text = (
                f"🙉 Выступление <b>{event.title}</b> возвращено\n"
                f"Будет отправлено {delivery_info.count} "
                f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}\n"
                f"Уникальный ID рассылки: <code>{delivery_info.delivery_id}</code>"
            )
        await callback.message.answer(
            text,
            reply_markup=InlineKeyboardBuilder(
                [
                    [
                        get_delete_delivery_button(delivery_info.delivery_id),
                    ]
                ]
            ).as_markup()
            if delivery_info.count > 0
            else None,
        )
        manager.show_mode = ShowMode.DELETE_AND_SEND
    except ServiceError as e:
        await callback.answer(e.message)
        return


async def move_event_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    app: AppHolder = dialog_manager.middleware_data["app"]
    if "/" in data and data.replace("/", "").isnumeric():
        try:
            event1, event2, delivery_info = await app.schedule_mgmt.move_event(
                event_id=dialog_manager.start_data,
                after_event_id=int(data.replace("/", "")),
            )
            await message.reply(
                f"✅ Выступление <b>{event1.title}</b> поставлено "
                f"после <b>{event2.title}</b>\n"
                f"Будет отправлено {delivery_info.count} "
                f"{pluralize(delivery_info.count, NOTIFICATIONS_PLURALS)}\n"
                f"Уникальный ID рассылки: <code>{delivery_info.delivery_id}</code>",
                reply_markup=InlineKeyboardBuilder(
                    [
                        [
                            get_delete_delivery_button(delivery_info.delivery_id),
                        ]
                    ]
                ).as_markup()
                if delivery_info.count > 0
                else None,
            )
            await dialog_manager.switch_to(
                states.EVENT_DETAILS.MAIN, show_mode=ShowMode.DELETE_AND_SEND
            )
        except ServiceError as e:
            await message.answer(e.message)
            dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
            return
    elif data.isnumeric():
        await show_event_page(dialog_manager, int(data))
    else:
        await set_search_query(dialog_manager, data)


async def set_counter_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    app: AppHolder = dialog_manager.middleware_data["app"]
    try:
        subscription = await app.subscriptions.create_subscription(
            CreateSubscriptionDTO(
                user_id=dialog_manager.event.from_user.id,
                event_id=dialog_manager.start_data,
                counter=data,
            ),
        )
    except ServiceError as e:
        await message.answer(e.message)
        dialog_manager.show_mode = ShowMode.DELETE_AND_SEND
        return
    await message.reply(
        f"✅ Подписка на выступление "
        f"<b>{subscription.event.title}</b> "
        f"успешно оформлена!",
    )
    await dialog_manager.switch_to(
        states.EVENT_DETAILS.MAIN, show_mode=ShowMode.DELETE_AND_SEND
    )


async def unsubscribe_button_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    try:
        subscription = await app.subscriptions.get_subscription_by_event(
            user_id=manager.event.from_user.id,
            event_id=manager.start_data,
        )
        await app.subscriptions.delete_subscription(subscription.id)
    except ServiceError as e:
        await callback.answer(e.message, show_alert=True)
        manager.show_mode = ShowMode.DELETE_AND_SEND
        return

    await callback.answer("🗑️ Подписка удалена!")
