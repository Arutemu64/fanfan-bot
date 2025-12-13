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
from fanfan.application.schedule.list_schedule import (
    ListSchedule,
    ListScheduleDTO,
)
from fanfan.application.voting.list_voting_participants import (
    GetVotingParticipantsDTO,
    ListVotingParticipants,
)
from fanfan.core.dto.page import Pagination
from fanfan.core.vo.nomination import NominationId
from fanfan.presentation.tgbot import states

router = Router(name="inline_query_router")

INLINE_DATA_SELECTED_NOMINATION_IDS = "inline_data_selected_nomination_ids"
INLINE_DATA_VOTING_NOMINATION_ID = "inline_data_voting_nomination_id"


@router.inline_query(StateFilter(states.InlineQuerySearch.EVENTS))
@inject
async def search_events(
    inline_query: InlineQuery, get_schedule_page: FromDishka[ListSchedule]
):
    offset = int(inline_query.offset) if inline_query.offset else 0
    page = await get_schedule_page(
        ListScheduleDTO(
            pagination=Pagination(
                limit=50,
                offset=offset,
            ),
            search_query=inline_query.query,
        )
    )
    results = [
        InlineQueryResultArticle(
            id=str(e.public_id),
            title=str(e.public_id),
            description=e.title,
            input_message_content=InputTextMessageContent(
                message_text=f"/{e.public_id}"
            ),
        )
        for e in page.items
    ]
    await inline_query.answer(
        results, cache_time=0, is_personal=True, next_offset=str(offset + 50)
    )


@router.inline_query(StateFilter(states.InlineQuerySearch.PARTICIPANTS))
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


@router.inline_query(StateFilter(states.InlineQuerySearch.VOTING_PARTICIPANTS))
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
