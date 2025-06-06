from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.application.schedule.read_schedule_page_for_user import (
    GetSchedulePageDTO,
    ReadSchedulePageForUser,
)
from fanfan.application.voting.read_participants_page_for_user import (
    GetParticipantsPageDTO,
    ReadParticipantsPageForUser,
)
from fanfan.core.dto.page import Pagination
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.voting.common import DATA_SELECTED_NOMINATION_ID

router = Router(name="inline_query_router")


@router.inline_query(StateFilter(states.InlineQuerySearch.EVENTS))
@inject
async def search_events(
    inline_query: InlineQuery, get_schedule_page: FromDishka[ReadSchedulePageForUser]
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


@router.inline_query(StateFilter(states.InlineQuerySearch.VOTING_PARTICIPANTS))
@inject
async def search_voting_participants(
    inline_query: InlineQuery,
    get_participants_page: FromDishka[ReadParticipantsPageForUser],
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
