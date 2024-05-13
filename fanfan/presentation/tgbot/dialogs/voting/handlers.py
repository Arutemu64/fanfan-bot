from typing import Any

from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import ManagedScroll
from aiogram_dialog.widgets.input import ManagedTextInput
from aiogram_dialog.widgets.kbd import Button

from fanfan.application.exceptions import ServiceError
from fanfan.application.exceptions.voting import VoteNotFound
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot import states

from .constants import (
    DATA_SEARCH_QUERY,
    DATA_SELECTED_NOMINATION_ID,
    DATA_USER_VOTE_ID,
    ID_VOTING_SCROLL,
)


async def select_nomination_handler(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str,
):
    dialog_manager.dialog_data[DATA_SELECTED_NOMINATION_ID] = item_id
    dialog_manager.dialog_data[DATA_SEARCH_QUERY] = None
    await dialog_manager.find(ID_VOTING_SCROLL).set_page(0)
    await dialog_manager.switch_to(states.VOTING.VOTING)


async def add_vote_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
):
    if "/" in data and data.replace("/", "").isnumeric():
        app: AppHolder = dialog_manager.middleware_data["app"]
        try:
            participant = await app.voting.get_participant_by_nomination_position(
                nomination_id=dialog_manager.dialog_data[DATA_SELECTED_NOMINATION_ID],
                nomination_position=int(data.replace("/", "")),
            )
            await app.voting.add_vote(
                user_id=dialog_manager.event.from_user.id,
                participant_id=participant.id,
                nomination_id=dialog_manager.dialog_data[DATA_SELECTED_NOMINATION_ID],
            )
        except ServiceError as e:
            await message.reply(e.message)
            return
    else:
        dialog_manager.dialog_data[DATA_SEARCH_QUERY] = data


async def cancel_vote_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    app: AppHolder = manager.middleware_data["app"]
    try:
        await app.voting.cancel_vote(manager.dialog_data[DATA_USER_VOTE_ID])
    except VoteNotFound:
        return
    except ServiceError as e:
        await callback.answer(e.message, show_alert=True)
        return


async def reset_search_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
):
    manager.dialog_data.pop(DATA_SEARCH_QUERY)


async def set_search_query_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    error: ValueError,
):
    dialog_manager.dialog_data[DATA_SEARCH_QUERY] = message.text
    scroll: ManagedScroll = dialog_manager.find(ID_VOTING_SCROLL)
    await scroll.set_page(0)
