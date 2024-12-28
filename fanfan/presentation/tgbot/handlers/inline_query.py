from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.application.events.get_schedule_page import (
    GetSchedulePage,
    GetSchedulePageDTO,
)
from fanfan.application.participants.get_participants_page import (
    GetParticipantsPage,
    GetParticipantsPageDTO,
)
from fanfan.core.dto.page import Pagination
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.voting.common import DATA_SELECTED_NOMINATION_ID

router = Router(name="inline_query_router")


@router.inline_query(StateFilter(states.InlineQuerySearch.events))
@inject
async def search_events(
    inline_query: InlineQuery, get_schedule_page: FromDishka[GetSchedulePage]
):
    offset = int(inline_query.offset) if inline_query.offset else 0
    page = await get_schedule_page(
        GetSchedulePageDTO(
            pagination=Pagination(
                limit=50,
                offset=offset,
            ),
            search_query=inline_query.query,
        )
    )
    results = [
        InlineQueryResultArticle(
            id=str(e.id),
            title=str(e.id),
            description=e.title,
            input_message_content=InputTextMessageContent(message_text=f"/{e.id}"),
        )
        for e in page.items
    ]
    await inline_query.answer(
        results, cache_time=0, is_personal=True, next_offset=str(offset + 50)
    )


@router.inline_query(StateFilter(states.InlineQuerySearch.voting_participants))
@inject
async def search_voting_participants(
    inline_query: InlineQuery,
    get_participants_page: FromDishka[GetParticipantsPage],
    state: FSMContext,
):
    offset = int(inline_query.offset) if inline_query.offset else 0
    page = await get_participants_page(
        GetParticipantsPageDTO(
            pagination=Pagination(
                limit=50,
                offset=offset,
            ),
            nomination_id=await state.get_value(DATA_SELECTED_NOMINATION_ID),
            search_query=inline_query.query,
            only_votable=True,
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
