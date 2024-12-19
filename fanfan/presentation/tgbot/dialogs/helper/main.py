from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Cancel, Start, Url
from aiogram_dialog.widgets.text import Const, Format
from dishka import AsyncContainer

from fanfan.adapters.config.models import Configuration
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings


async def helper_main_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
):
    config: Configuration = await container.get(Configuration)
    return {
        "docs_link": config.docs_link,
    }


helper_main_window = Window(
    Title(Const(strings.titles.helper_menu)),
    Const("Для волонтёров доступны следующие функции:\n"),
    Const(
        "<b>🧰 Инструменты волонтёра</b> в <code>📅 Программе</code> - "
        "Вы можете отмечать выступления на сцене как текущие, а также "
        "переносить и пропускать их.\n",
    ),
    Const(
        "<b>🔍 Найти пользователя</b> - если <code>🤳 QR-сканер</code> в главном меню "
        "не работает, вы можете найти пользователя вручную по его @никнейму или ID. "
        "Найдя пользователя, Вы можете добавить ему очков или отметить достижение "
        "как полученное",
    ),
    Start(
        state=states.UserManager.manual_user_search,
        id="user_search",
        text=Const("🔍 Найти пользователя"),
    ),
    Url(
        text=Const(strings.buttons.help_page),
        url=Format("{docs_link}"),
        when="docs_link",
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Helper.main,
    getter=helper_main_getter,
)
