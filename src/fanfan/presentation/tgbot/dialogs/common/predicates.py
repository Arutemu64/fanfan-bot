from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable

from fanfan.core.models.user import UserData
from fanfan.core.vo.user import UserRole


def is_helper(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    user: UserData = manager.middleware_data["user"]
    return user.role in [UserRole.HELPER, UserRole.ORG]


def is_org(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    user: UserData = manager.middleware_data["user"]
    return user.role is UserRole.ORG


def is_ticket_linked(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    user: UserData = manager.middleware_data["user"]
    return bool(user.ticket)
