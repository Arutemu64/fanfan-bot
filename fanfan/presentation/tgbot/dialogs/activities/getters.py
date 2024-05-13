from aiogram_dialog import DialogManager

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.holder import AppHolder

from .constants import DATA_SELECTED_ACTIVITY_ID, ID_ACTIVITIES_SCROLL


async def activities_getter(
    dialog_manager: DialogManager, app: AppHolder, user: FullUserDTO, **kwargs
):
    page = await app.activities.get_activities_page(
        page_number=await dialog_manager.find(ID_ACTIVITIES_SCROLL).get_page(),
        activities_per_page=user.settings.items_per_page,
    )
    return {
        "activities_list": [(a.id, a.title) for a in page.items],
        "pages": page.total_pages,
    }


async def activity_info_getter(
    dialog_manager: DialogManager, app: AppHolder, user: FullUserDTO, **kwargs
):
    activity = await app.activities.get_activity(
        dialog_manager.dialog_data[DATA_SELECTED_ACTIVITY_ID]
    )
    return {
        "title": activity.title,
        "description": activity.description,
        "subtext": activity.subtext,
        "image_path": activity.image_path,
    }
