from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.application.participants.list_participants import (
    ListParticipants,
    ListParticipantsDTO,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.vo.nomination import NominationId
from fanfan.presentation.tgbot import states

INLINE_DATA_SELECTED_NOMINATION_IDS = "inline_data_selected_nomination_ids"

participants_handlers_router = Router(name="participants_router")


@participants_handlers_router.inline_query(
    StateFilter(states.InlineQuerySearch.PARTICIPANTS)
)
@inject
async def search_participants(
    inline_query: InlineQuery,
    list_participants: FromDishka[ListParticipants],
    state: FSMContext,
):
    offset = int(inline_query.offset) if inline_query.offset else 0
    nomination_ids: list[NominationId] = await state.get_value(
        INLINE_DATA_SELECTED_NOMINATION_IDS
    )
    page = await list_participants(
        ListParticipantsDTO(
            pagination=Pagination(
                limit=50,
                offset=offset,
            ),
            search_query=inline_query.query,
            nomination_ids=nomination_ids,
        ),
    )
    results = [
        InlineQueryResultArticle(
            id=str(p.id),
            title=str(p.id),
            description=p.title,
            input_message_content=InputTextMessageContent(message_text=f"/{p.id}"),
        )
        for p in page.items
    ]
    await inline_query.answer(
        results, cache_time=0, is_personal=True, next_offset=str(offset + 50)
    )
