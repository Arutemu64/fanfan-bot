from aiogram_dialog import DialogManager

from fanfan.application.dto.user import FullUserDTO


async def user_info_getter(dialog_manager: DialogManager, user: FullUserDTO, **kwargs):
    return {
        "user": user,
        "user_info_list": [
            ("Никнейм:", user.username),
            ("ID:", user.id),
            (
                "Билет:",
                user.ticket.id if user.ticket else "не привязан",
            ),
            ("Роль:", user.role.label),
        ],
    }
