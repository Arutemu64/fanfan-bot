from aiogram_dialog import DialogManager

from fanfan.application.holder import AppHolder

from .constants import DATA_USER_ID, ID_ACHIEVEMENTS_SCROLL


async def achievements_getter(
    dialog_manager: DialogManager,
    app: AppHolder,
    **kwargs,
):
    user = await app.users.get_user_by_id(dialog_manager.dialog_data[DATA_USER_ID])
    page = await app.quest.get_achievements_page(
        page_number=await dialog_manager.find(ID_ACHIEVEMENTS_SCROLL).get_page(),
        achievements_per_page=user.settings.items_per_page,
        user_id=user.id,
    )
    return {
        "achievements": page.items,
        "pages": page.total_pages,
        "showing_self": user.id == dialog_manager.event.from_user.id,
    }
