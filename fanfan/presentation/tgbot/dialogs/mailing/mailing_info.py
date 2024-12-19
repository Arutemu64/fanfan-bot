from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.kbd import Button, Cancel
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import AsyncContainer

from fanfan.application.mailing.cancel_mailing import CancelMailing
from fanfan.application.mailing.get_mailing_info import GetMailingInfo
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.core.models.mailing import MailingId, MailingStatus
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.mailing.common import DATA_MAILING_ID
from fanfan.presentation.tgbot.static import strings


async def mailing_info_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    get_mailing_info: GetMailingInfo = await container.get(GetMailingInfo)
    get_user_by_id: GetUserById = await container.get(GetUserById)

    mailing_info = await get_mailing_info(dialog_manager.start_data[DATA_MAILING_ID])
    sender = await get_user_by_id(mailing_info.data.by_user_id)

    return {
        "id": mailing_info.data.id,
        "total": mailing_info.data.total,
        "processed": mailing_info.data.processed,
        "status": mailing_info.status,
        "sent": mailing_info.sent,
        "sender": sender,
    }


async def cancel_mailing_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    cancel_mailing: CancelMailing = await container.get(CancelMailing)
    await cancel_mailing(manager.start_data[DATA_MAILING_ID])
    await callback.answer("✅ Рассылка отменена")


mailing_info_window = Window(
    Title(Const("📨 Информация о рассылке")),
    Jinja("<b>ID:</b> <code>{{ id }}</code>"),
    Jinja("<b>Обработано:</b> {{ processed }} из {{ total }}"),
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
    state=states.Mailing.mailing_info,
)


async def show_mailing_info(manager: DialogManager, mailing_id: MailingId) -> None:
    await manager.start(
        state=states.Mailing.mailing_info,
        data={DATA_MAILING_ID: mailing_id},
        show_mode=ShowMode.SEND,
    )
