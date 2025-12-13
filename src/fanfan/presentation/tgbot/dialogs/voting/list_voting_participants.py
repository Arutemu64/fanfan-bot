from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.voting.add_vote import AddVote, AddVoteDTO
from fanfan.application.voting.cancel_vote import CancelVote, CancelVoteDTO
from fanfan.application.voting.get_voting_nomination_by_id import (
    GetVotingNominationById,
    GetVotingNominationByIdDTO,
)
from fanfan.application.voting.get_voting_state import GetVotingState
from fanfan.application.voting.list_voting_participants import (
    GetVotingParticipantsDTO,
    ListVotingParticipants,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.user import FullUserDTO
from fanfan.core.exceptions.votes import VoteNotFound
from fanfan.core.services.voting import VotingState
from fanfan.core.vo.participant import ParticipantVotingNumber
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_dialog_data_adapter
from fanfan.presentation.tgbot.dialogs.common.widgets import (
    SwitchInlineQueryCurrentChat,
    Title,
)
from fanfan.presentation.tgbot.dialogs.voting.data import (
    VotingDialogData,
)
from fanfan.presentation.tgbot.middlewares.dialog_data_adapter import DialogDataAdapter
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import voting_list

ID_VOTING_SCROLL = "voting_scroll"


@inject
async def list_voting_participants_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    dialog_data_adapter: DialogDataAdapter,
    get_voting_nomination_by_id: FromDishka[GetVotingNominationById],
    get_voting_participants_page: FromDishka[ListVotingParticipants],
    get_voting_state: FromDishka[GetVotingState],
    **kwargs,
) -> dict:
    dialog_data = dialog_data_adapter.load(VotingDialogData)
    nomination = await get_voting_nomination_by_id(
        GetVotingNominationByIdDTO(nomination_id=dialog_data.nomination_id)
    )
    dialog_data.user_vote_id = nomination.vote_id
    dialog_data_adapter.flush(dialog_data)
    page = await get_voting_participants_page(
        GetVotingParticipantsDTO(
            pagination=Pagination(
                limit=current_user.settings.items_per_page,
                offset=await dialog_manager.find(ID_VOTING_SCROLL).get_page()
                * current_user.settings.items_per_page,
            ),
            nomination_id=dialog_data.nomination_id,
        ),
    )
    pages = page.total // current_user.settings.items_per_page + bool(
        page.total % current_user.settings.items_per_page
    )
    voting_state = await get_voting_state()
    return {
        # Participants
        "nomination_title": nomination.title,
        "participants": page.items,
        "pages": pages or 1,
        # Voting state
        "voting_state": voting_state,
        "can_vote": voting_state is VotingState.OPEN,
        "is_voted": bool(dialog_data.user_vote_id),
    }


@inject
async def add_vote_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
    add_vote: FromDishka[AddVote],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(dialog_manager)
    dialog_data = dialog_data_adapter.load(VotingDialogData)
    if "/" in data and data.replace("/", "").isnumeric():
        await add_vote(
            AddVoteDTO(
                nomination_id=dialog_data.nomination_id,
                voting_number=ParticipantVotingNumber(int(data.replace("/", ""))),
            )
        )


@inject
async def cancel_vote_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    cancel_vote: FromDishka[CancelVote],
) -> None:
    dialog_data_adapter = get_dialog_data_adapter(manager)
    dialog_data = dialog_data_adapter.load(VotingDialogData)
    try:
        await cancel_vote(CancelVoteDTO(vote_id=dialog_data.user_vote_id))
    except VoteNotFound:
        return


voting_participants_window = Window(
    Title(Jinja("🌟 Номинация {{ nomination_title }}")),
    Jinja(voting_list),
    Case(
        {
            VotingState.OPEN: Const(
                "👆 Чтобы проголосовать, нажми на номер участника", when=~F["is_voted"]
            ),
            VotingState.NO_TICKET: Const("🔒 Привяжи билет для голосования"),
            VotingState.DISABLED: Const("🔒 Голосование отключено"),
        },
        selector="voting_state",
    ),
    SwitchInlineQueryCurrentChat(
        text=Const(strings.buttons.search),
        switch_inline_query=Const(""),
        when=~F["is_voted"] & F["can_vote"],
    ),
    Row(
        StubScroll(ID_VOTING_SCROLL, pages="pages"),
        FirstPage(scroll=ID_VOTING_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_VOTING_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_VOTING_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_VOTING_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_VOTING_SCROLL, text=Const("⏭️")),
    ),
    Button(
        Const("🗑️ Отменить голос"),
        id="cancel_vote",
        when=F["is_voted"] & F["can_vote"],
        on_click=cancel_vote_handler,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.Voting.LIST_NOMINATIONS,
        id="nominations",
    ),
    TextInput(
        id="vote_id_input",
        type_factory=str,
        on_success=add_vote_handler,
    ),
    state=states.Voting.ADD_VOTE,
    getter=list_voting_participants_getter,
)
