from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import Whenable

from fanfan.core.vo.user import UserRole
from fanfan.presentation.tgbot.dialogs.common.utils import get_current_user


def is_helper(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    current_user = get_current_user(manager)
    return current_user.role in [UserRole.HELPER, UserRole.ORG]


def is_org(data: dict, widget: Whenable, manager: DialogManager) -> bool:
    current_user = get_current_user(manager)
    return current_user.role is UserRole.ORG
