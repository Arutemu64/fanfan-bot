from dataclasses import dataclass

from fanfan.core.vo.mailing import MailingId
from fanfan.core.vo.telegram import TelegramFileId


@dataclass(slots=True)
class MailingDialogData:
    mailing_id: MailingId | None = None

    # Create mailing
    text: str | None = None
    image_id: TelegramFileId | None = None
