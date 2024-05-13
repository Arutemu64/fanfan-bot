from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import ManagedCheckbox

from fanfan.application.holder import AppHolder

from .constants import DATA_FEEDBACK_TEXT, ID_ASAP_CHECKBOX


async def feedback_window_getter(
    dialog_manager: DialogManager, app: AppHolder, **kwargs
):
    asap_checkbox: ManagedCheckbox = dialog_manager.find(ID_ASAP_CHECKBOX)
    settings = await app.settings.get_settings()
    return {
        "sending_allowed": dialog_manager.dialog_data.get(DATA_FEEDBACK_TEXT),
        "asap_feedback_enabled": settings.asap_feedback_enabled,
        "asap": asap_checkbox.is_checked(),
        "feedback_text": dialog_manager.dialog_data.get(DATA_FEEDBACK_TEXT)
        or "<i>отправь сообщение, чтобы ввести/изменить текст</i>",
    }
