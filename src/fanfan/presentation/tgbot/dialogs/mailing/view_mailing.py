from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.notifications.cancel_mailing import (
    CancelMailing,
    CancelMailingDTO,
)
from fanfan.application.notifications.get_mailing_info import (
    GetMailingInfo,
    GetMailingInfoDTO,
)
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.core.vo.mailing import MailingStatus
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.mailing.data import MailingDialogData
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter
from fanfan.presentation.tgbot.static import strings


@inject
async def mailing_info_getter(
    dialog_manager: DialogManager,
    dialog_data_adapter: DialogDataAdapter,
    get_mailing_info: FromDishka[GetMailingInfo],
    get_user_by_id: FromDishka[GetUserById],
    **kwargs,
) -> dict:
    dialog_data = dialog_data_adapter.load(MailingDialogData)
    mailing_info = await get_mailing_info(
        GetMailingInfoDTO(mailing_id=dialog_data.mailing_id)
    )
    sender = await get_user_by_id(mailing_info.data.by_user_id)
    return {
        "id": mailing_info.data.id,
        "total_messages": mailing_info.data.total_messages,
        "messages_processed": mailing_info.data.messages_processed,
        "status": mailing_info.status,
        "sent": mailing_info.sent,
        "sender": sender,
    }


@inject
async def cancel_mailing_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    cancel_mailing: FromDishka[CancelMailing],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(MailingDialogData)
    await cancel_mailing(CancelMailingDTO(mailing_id=dialog_data.mailing_id))
    await callback.answer("✅ Рассылка отменена")


mailing_info_window = Window(
    Title(Const("📨 Информация о рассылке")),
    Jinja("<b>ID:</b> <code>{{ id }}</code>"),
    Jinja("<b>Обработано:</b> {{ messages_processed }} из {{ total_messages }}"),
    Jinja("<b>Сообщений в БД:</b> {{ sent }}"),
    Jinja("<b>Статус:</b> {{ status }}"),
    Jinja("<b>Отправил:</b> @{{ sender.username }} ({{ sender.id }})"),
    Button(
        Const("🗑️ Отменить рассылку"),
        when=F["status"].is_not(MailingStatus.CANCELLED),
        id="cancel_mailing",
        on_click=cancel_mailing_handler,
    ),
    Button(Const(strings.buttons.update), id="update"),
    Cancel(Const(strings.buttons.back)),
    getter=mailing_info_getter,
    state=states.Mailing.MAILING_INFO,
)
