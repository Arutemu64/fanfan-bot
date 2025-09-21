from aiogram_dialog import DialogManager, ShowMode

from fanfan.core.vo.mailing import MailingId
from fanfan.presentation.tgbot import states


async def show_mailing_info(manager: DialogManager, mailing_id: MailingId) -> None:
    await manager.start(
        state=states.Mailing.MAILING_INFO,
        data={"mailing_id": mailing_id},
        show_mode=ShowMode.SEND,
    )
