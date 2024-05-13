from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from aiogram_dialog.widgets.kbd import ManagedMultiselect

from fanfan.common.enums import UserRole

from .constants import (
    DATA_IMAGE_ID,
    DATA_TEXT,
    ID_ROLES_PICKER,
)


async def create_delivery_getter(dialog_manager: DialogManager, **kwargs):
    roles_picker: ManagedMultiselect[UserRole] = dialog_manager.find(ID_ROLES_PICKER)
    notification_text = dialog_manager.dialog_data.get(DATA_TEXT) or "не задан"
    if dialog_manager.dialog_data.get(DATA_IMAGE_ID):
        image = MediaAttachment(
            type=ContentType.PHOTO,
            file_id=MediaId(dialog_manager.dialog_data.get(DATA_IMAGE_ID)),
        )
    else:
        image = None
    return {
        "notification_text": notification_text,
        "image": image,
        "sending_allowed": dialog_manager.dialog_data.get(DATA_TEXT)
        and len(roles_picker.get_checked()) > 0,
    }
