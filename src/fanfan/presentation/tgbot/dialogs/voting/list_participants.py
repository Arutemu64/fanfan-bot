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
from aiogram_dialog.widgets.text import Const, Format, Jinja
from dishka import AsyncContainer

from fanfan.application.voting.add_vote import AddVote, AddVoteDTO
from fanfan.application.voting.cancel_vote import CancelVote, CancelVoteDTO
from fanfan.application.voting.read_nomination_for_user import ReadNominationForUser
from fanfan.application.voting.read_participants_page_for_user import (
    GetParticipantsPageDTO,
    ReadParticipantsPageForUser,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.exceptions.votes import VoteNotFound
from fanfan.core.models.user import UserData
from fanfan.core.vo.participant import ParticipantVotingNumber
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import (
    SwitchInlineQueryCurrentChat,
    Title,
)
from fanfan.presentation.tgbot.dialogs.voting.common import (
    DATA_SELECTED_NOMINATION_ID,
)
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import voting_list

ID_VOTING_SCROLL = "voting_scroll"
DATA_USER_VOTE_ID = "user_vote_id"


async def participants_getter(
    dialog_manager: DialogManager,
    user: UserData,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    get_nomination_by_id: ReadNominationForUser = await container.get(
        ReadNominationForUser
    )
    get_participants_page: ReadParticipantsPageForUser = await container.get(
        ReadParticipantsPageForUser
    )

    nomination = await get_nomination_by_id(
        dialog_manager.dialog_data[DATA_SELECTED_NOMINATION_ID],
    )
    page = await get_participants_page(
        GetParticipantsPageDTO(
            pagination=Pagination(
                limit=user.settings.items_per_page,
                offset=await dialog_manager.find(ID_VOTING_SCROLL).get_page()
                * user.settings.items_per_page,
            ),
            nomination_id=dialog_manager.dialog_data[DATA_SELECTED_NOMINATION_ID],
        ),
    )
    pages = page.total // user.settings.items_per_page + bool(
        page.total % user.settings.items_per_page
    )
    dialog_manager.dialog_data[DATA_USER_VOTE_ID] = (
        nomination.vote_id if nomination.vote_id else None
    )
    return {
        "nomination_title": nomination.title,
        "participants": page.items,
        "pages": pages or 1,
        "is_voted": bool(dialog_manager.dialog_data[DATA_USER_VOTE_ID]),
    }


async def add_vote_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    add_vote: AddVote = await container.get(AddVote)

    if "/" in data and data.replace("/", "").isnumeric():
        await add_vote(
            AddVoteDTO(
                nomination_id=dialog_manager.dialog_data[DATA_SELECTED_NOMINATION_ID],
                voting_number=ParticipantVotingNumber(int(data.replace("/", ""))),
            )
        )


async def cancel_vote_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    cancel_vote: CancelVote = await container.get(CancelVote)

    try:
        await cancel_vote(CancelVoteDTO(vote_id=manager.dialog_data[DATA_USER_VOTE_ID]))
    except VoteNotFound:
        return


voting_window = Window(
    Title(Jinja("🌟 Номинация {{ nomination_title }}")),
    Jinja(voting_list),
    Const("👆 Чтобы проголосовать, нажми на номер участника", when=~F["is_voted"]),
    SwitchInlineQueryCurrentChat(
        text=Const(strings.buttons.search),
        switch_inline_query=Const(""),
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
        when="is_voted",
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
    getter=participants_getter,
)
