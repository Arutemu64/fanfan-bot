from aiogram import Router
from aiogram.filters import Command, StateFilter
from aiogram.types import (
    CallbackQuery,
    InlineQuery,
    InlineQueryResultArticle,
    InputTextMessageContent,
    Message,
)
from aiogram_dialog import DialogManager, ShowMode
from dishka import FromDishka
from dishka.integrations.aiogram import inject

from fanfan.application.schedule.list_schedule import ListSchedule, ListScheduleDTO
from fanfan.application.schedule.management.revert_change import (
    RevertScheduleChange,
    RevertScheduleChangeDTO,
)
from fanfan.core.dto.page import Pagination
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.filters.callbacks import (
    OpenSubscriptionsCallback,
    UndoScheduleChangeCallback,
)
from fanfan.presentation.tgbot.filters.commands import NOTIFICATIONS_CMD, SCHEDULE_CMD

schedule_handlers_router = Router(name="schedule_handlers_router")


@schedule_handlers_router.message(Command(SCHEDULE_CMD))
async def schedule_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Schedule.MAIN)


@schedule_handlers_router.message(Command(NOTIFICATIONS_CMD))
async def notifications_cmd(message: Message, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(states.Schedule.SUBSCRIPTIONS)


@schedule_handlers_router.inline_query(StateFilter(states.InlineQuerySearch.EVENTS))
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


@schedule_handlers_router.callback_query(OpenSubscriptionsCallback.filter())
async def open_subscriptions_menu(
    query: CallbackQuery,
    dialog_manager: DialogManager,
) -> None:
    await dialog_manager.start(
        state=states.Schedule.SUBSCRIPTIONS,
        show_mode=ShowMode.SEND,
    )


@schedule_handlers_router.callback_query(UndoScheduleChangeCallback.filter())
@inject
async def undo_schedule_change(
    query: CallbackQuery,
    callback_data: UndoScheduleChangeCallback,
    interactor: FromDishka[RevertScheduleChange],
):
    await interactor(
        RevertScheduleChangeDTO(schedule_change_id=callback_data.schedule_change_id)
    )
    await query.answer()
