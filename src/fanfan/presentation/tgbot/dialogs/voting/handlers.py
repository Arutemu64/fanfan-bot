from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from aiogram_dialog import DialogManager
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.application.voting.list_voting_participants import (
    GetVotingParticipantsDTO,
    ListVotingParticipants,
)
from fanfan.core.dto.page import Pagination
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters.commands import VOTING_CMD

INLINE_DATA_VOTING_NOMINATION_ID = "inline_data_voting_nomination_id"

voting_handlers_router = Router(name="voting_handlers_router")


@voting_handlers_router.message(Command(VOTING_CMD))
async def voting_cmd(
    message: Message,
    dialog_manager: DialogManager,
) -> None:
    await dialog_manager.start(states.Voting.LIST_NOMINATIONS)


@voting_handlers_router.inline_query(
    StateFilter(states.InlineQuerySearch.VOTING_PARTICIPANTS)
)
@inject
async def search_voting_participants(
    inline_query: InlineQuery,
    get_participants_page: FromDishka[ListVotingParticipants],
    state: FSMContext,
):
    offset = int(inline_query.offset) if inline_query.offset else 0
    page = await get_participants_page(
        GetVotingParticipantsDTO(
            pagination=Pagination(
                limit=50,
                offset=offset,
            ),
            nomination_id=await state.get_value(INLINE_DATA_VOTING_NOMINATION_ID),
            search_query=inline_query.query,
        ),
    )
    results = [
        InlineQueryResultArticle(
            id=str(p.voting_number),
            title=str(p.voting_number),
            description=p.title,
            input_message_content=InputTextMessageContent(
                message_text=f"/{p.voting_number}"
            ),
        )
        for p in page.items
    ]
    await inline_query.answer(
        results, cache_time=0, is_personal=True, next_offset=str(offset + 50)
    )
