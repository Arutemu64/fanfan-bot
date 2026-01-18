import operator
import typing
from typing import Any

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
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.voting.list_voting_nominations import (
    ListVotingNominations,
    ListVotingNominationsDTO,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.vo.nomination import NominationId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.dialogs.voting.data import (
    VotingDialogData,
)
from fanfan.presentation.tgbot.dialogs.voting.list_voting_participants import (
    ID_VOTING_SCROLL,
)
from fanfan.presentation.tgbot.handlers.voting import (
    INLINE_DATA_VOTING_NOMINATION_ID,
)
from fanfan.presentation.tgbot.static import strings

if typing.TYPE_CHECKING:
    from aiogram.fsm.context import FSMContext

ID_NOMINATIONS_SCROLL = "nominations_scroll"


@inject
async def list_voting_nominations_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    get_voting_nominations: FromDishka[ListVotingNominations],
    **kwargs,
) -> dict:
    page = await get_voting_nominations(
        ListVotingNominationsDTO(
            pagination=Pagination(
                limit=current_user.settings.items_per_page,
                offset=await dialog_manager.find(ID_NOMINATIONS_SCROLL).get_page()
                * current_user.settings.items_per_page,
            )
        )
    )
    nominations_list = [(n.id, n) for n in page.items]
    pages = page.total // current_user.settings.items_per_page + bool(
        page.total % current_user.settings.items_per_page
    )
    return {
        "nominations_list": nominations_list,
        "pages": pages or 1,
    }


async def select_voting_nomination_handler(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: int,
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(VotingDialogData)

    dialog_data.nomination_id = NominationId(item_id)
    dialog_data_adapter.flush(dialog_data)

    # Enable search
    state: FSMContext = dialog_manager.middleware_data["state"]
    await state.update_data({INLINE_DATA_VOTING_NOMINATION_ID: item_id})
    await state.set_state(states.InlineQuerySearch.VOTING_PARTICIPANTS)

    await dialog_manager.find(ID_VOTING_SCROLL).set_page(0)
    await dialog_manager.switch_to(states.Voting.ADD_VOTE)


voting_nominations_window = Window(
    Title(Const(strings.titles.voting)),
    Const("Для голосования доступны следующие номинации\n"),
    Const("📺 AMV: https://vkvideo.ru/playlist/-32133918_52319783"),
    Const("🖼️ Арт: https://fancom.info/cards/topic/art"),
    Const("📸 Фотокосплей: https://fancom.info/cards/topic/fotcosp"),
    Column(
        Select(
            Jinja("{{item[1].title}} {% if item[1].vote_id %}✅{% endif %}"),
            id="nomination",
            item_id_getter=operator.itemgetter(0),
            items="nominations_list",
            type_factory=int,
            on_click=select_voting_nomination_handler,
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
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.Voting.LIST_NOMINATIONS,
    getter=list_voting_nominations_getter,
)
