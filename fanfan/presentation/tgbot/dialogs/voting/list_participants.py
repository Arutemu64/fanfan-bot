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

from fanfan.application.nominations.get_nomination_by_id import GetNominationById
from fanfan.application.participants.get_participant_by_scoped_id import (
    GetScopedParticipant,
    GetScopedParticipantDTO,
)
from fanfan.application.participants.get_participants_page import (
    GetParticipantsPage,
    GetParticipantsPageDTO,
)
from fanfan.application.votes.add_vote import AddVote
from fanfan.application.votes.cancel_vote import CancelVote
from fanfan.core.exceptions.base import AppException
from fanfan.core.exceptions.votes import VoteNotFound
from fanfan.core.models.page import Pagination
from fanfan.core.models.participant import ParticipantScopedId
from fanfan.core.models.user import FullUserModel
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import (
    SwitchInlineQueryCurrentChat,
    Title,
)
from fanfan.presentation.tgbot.dialogs.voting.common import (
    DATA_SELECTED_NOMINATION_ID,
)
from fanfan.presentation.tgbot.static.templates import voting_list
from fanfan.presentation.tgbot.ui import strings

ID_VOTING_SCROLL = "voting_scroll"
DATA_USER_VOTE_ID = "user_vote_id"


async def participants_getter(
    dialog_manager: DialogManager,
    user: FullUserModel,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    get_nomination_by_id: GetNominationById = await container.get(GetNominationById)
    get_participants_page: GetParticipantsPage = await container.get(
        GetParticipantsPage
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
    dialog_manager.dialog_data[DATA_USER_VOTE_ID] = (
        nomination.user_vote.id if nomination.user_vote else None
    )
    return {
        "nomination_title": nomination.title,
        "participants": page.items,
        "pages": page.total // user.settings.items_per_page
        + bool(page.total % user.settings.items_per_page),
        "voted": bool(dialog_manager.dialog_data[DATA_USER_VOTE_ID]),
    }


async def add_vote_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    add_vote: AddVote = await container.get(AddVote)
    get_participant_by_scoped_id: GetScopedParticipant = await container.get(
        GetScopedParticipant
    )

    if "/" in data and data.replace("/", "").isnumeric():
        try:
            participant = await get_participant_by_scoped_id(
                GetScopedParticipantDTO(
                    nomination_id=dialog_manager.dialog_data[
                        DATA_SELECTED_NOMINATION_ID
                    ],
                    scoped_id=ParticipantScopedId(int(data.replace("/", ""))),
                )
            )
            await add_vote(participant.id)
        except AppException as e:
            await message.reply(e.message)
            return


async def cancel_vote_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    cancel_vote: CancelVote = await container.get(CancelVote)

    try:
        await cancel_vote(manager.dialog_data[DATA_USER_VOTE_ID])
    except VoteNotFound:
        return
    except AppException as e:
        await callback.answer(e.message, show_alert=True)
        return


voting_window = Window(
    Title(Format("🎖️ Номинация {nomination_title}")),
    Jinja(voting_list),
    Const("👆 Чтобы проголосовать, нажми на номер участника", when=~F["voted"]),
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
        when=F["pages"] > 1,
    ),
    TextInput(
        id="vote_id_input",
        type_factory=str,
        on_success=add_vote_handler,
    ),
    Button(
        Const("🗑️ Отменить голос"),
        id="cancel_vote",
        when="voted",
        on_click=cancel_vote_handler,
    ),
    SwitchInlineQueryCurrentChat(
        text=Const(strings.buttons.search),
        switch_inline_query=Const(""),
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.Voting.list_nominations,
        id="nominations",
    ),
    state=states.Voting.add_vote,
    getter=participants_getter,
)
