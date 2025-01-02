from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Cancel, Start, Url, WebApp
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
        "qr_scanner_url": config.web.build_qr_scanner_url() if config.web else None,
    }


helper_main_window = Window(
    Title(Const(strings.titles.helper_menu)),
    WebApp(
        Const(strings.titles.qr_scanner),
        url=Format("{qr_scanner_url}"),
        when="qr_scanner_url",
    ),
    Start(
        state=states.UserManager.MANUAL_USER_SEARCH,
        id="user_search",
        text=Const("🔍 Найти пользователя"),
    ),
    Url(
        text=Const(strings.buttons.help_page),
        url=Format("{docs_link}"),
        when="docs_link",
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Helper.MAIN,
    getter=helper_main_getter,
)
