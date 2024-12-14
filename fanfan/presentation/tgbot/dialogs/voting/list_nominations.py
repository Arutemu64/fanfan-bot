import operator
import typing
from typing import Any

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Cancel,
    Column,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    Select,
    StubScroll,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja
from dishka import AsyncContainer

from fanfan.application.nominations.get_nominations_page import GetNominationsPage
from fanfan.core.dto.page import Pagination
from fanfan.core.models.user import FullUser
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.voting.common import (
    DATA_SELECTED_NOMINATION_ID,
)
from fanfan.presentation.tgbot.dialogs.voting.list_participants import ID_VOTING_SCROLL
from fanfan.presentation.tgbot.ui import strings

if typing.TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

ID_NOMINATIONS_SCROLL = "nominations_scroll"


async def nominations_getter(
    dialog_manager: DialogManager,
    user: FullUser,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    get_nominations_page: GetNominationsPage = await container.get(GetNominationsPage)

    page = await get_nominations_page(
        only_votable=True,
        pagination=Pagination(
            limit=user.settings.items_per_page,
            offset=await dialog_manager.find(ID_NOMINATIONS_SCROLL).get_page()
            * user.settings.items_per_page,
        ),
    )
    nominations_list = [(n.id, n) for n in page.items]
    return {
        "nominations_list": nominations_list,
        "pages": page.total // user.settings.items_per_page
        + bool(page.total % user.settings.items_per_page),
    }


async def select_nomination_handler(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: int,
) -> None:
    state: FSMContext = dialog_manager.middleware_data["state"]

    dialog_manager.dialog_data[DATA_SELECTED_NOMINATION_ID] = item_id

    # Enable search
    await state.update_data({DATA_SELECTED_NOMINATION_ID: item_id})
    await state.set_state(states.InlineQuerySearch.voting_participants)

    await dialog_manager.find(ID_VOTING_SCROLL).set_page(0)
    await dialog_manager.switch_to(states.Voting.add_vote)


nominations_window = Window(
    Title(Const(strings.titles.voting)),
    Const("Для голосования доступны следующие номинации"),
    Column(
        Select(
            Jinja("{{item[1].title}} {% if item[1].user_vote %}✅{% endif %}"),
            id="nomination",
            item_id_getter=operator.itemgetter(0),
            items="nominations_list",
            type_factory=int,
            on_click=select_nomination_handler,
        ),
    ),
    StubScroll(ID_NOMINATIONS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_NOMINATIONS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("⏭️")),
        when=F["pages"] > 1,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Voting.list_nominations,
    getter=nominations_getter,
)
