import typing

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable

from fanfan.core.enums import UserRole

if typing.TYPE_CHECKING:
    from fanfan.core.models.user import FullUserModel


def is_helper(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    user: FullUserModel = manager.middleware_data["user"]
    return user.role in [UserRole.HELPER, UserRole.ORG]


def is_org(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    user: FullUserModel = manager.middleware_data["user"]
    return user.role is UserRole.ORG


def is_ticket_linked(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    user: FullUserModel = manager.middleware_data["user"]
    return bool(user.ticket)
