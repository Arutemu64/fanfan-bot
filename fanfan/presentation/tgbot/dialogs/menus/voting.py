import operator
from typing import Any

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.input.text import ManagedTextInput
from aiogram_dialog.widgets.kbd import (
    Button,
    Cancel,
    Column,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    Select,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions import ServiceError
from fanfan.application.exceptions.voting import VoteNotFound
from fanfan.application.holder import AppHolder
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.static.templates import voting_list
from fanfan.presentation.tgbot.ui import strings

ID_NOMINATIONS_SCROLL = "nominations_scroll"
ID_VOTING_SCROLL = "voting_scroll"

DATA_CURRENT_NOMINATION_ID = "current_nomination_id"
DATA_USER_VOTE_ID = "user_vote"


async def nominations_getter(
    dialog_manager: DialogManager,
    user: FullUserDTO,
    app: AppHolder,
    **kwargs,
):
    page = await app.voting.get_nominations_page(
        page_number=await dialog_manager.find(ID_NOMINATIONS_SCROLL).get_page(),
        nominations_per_page=user.settings.items_per_page,
        user_id=user.id,
    )
    nominations_list = []
    for nomination in page.items:
        nominations_list.append(
            (
                nomination.id,
                f"{nomination.title} ✅" if nomination.user_vote else nomination.title,
            ),
        )
    return {
        "nominations_list": nominations_list,
        "pages": page.total_pages,
    }


async def participants_getter(
    dialog_manager: DialogManager,
    user: FullUserDTO,
    app: AppHolder,
    **kwargs,
):
    nomination = await app.voting.get_nomination(
        dialog_manager.dialog_data[DATA_CURRENT_NOMINATION_ID],
    )
    page = await app.voting.get_participants_page(
        nomination_id=dialog_manager.dialog_data[DATA_CURRENT_NOMINATION_ID],
        page_number=await dialog_manager.find(ID_VOTING_SCROLL).get_page(),
        participants_per_page=user.settings.items_per_page,
        user_id=user.id,
    )
    try:
        user_vote = await app.voting.get_vote_by_nomination(
            user_id=user.id,
            nomination_id=dialog_manager.dialog_data[DATA_CURRENT_NOMINATION_ID],
        )
        dialog_manager.dialog_data[DATA_USER_VOTE_ID] = user_vote.id
    except VoteNotFound:
        dialog_manager.dialog_data[DATA_USER_VOTE_ID] = None
    return {
        "nomination_title": nomination.title,
        "pages": page.total_pages,
        "participants": page.items,
        "voted": True if dialog_manager.dialog_data[DATA_USER_VOTE_ID] else False,
    }


async def select_nomination_handler(
    callback: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    item_id: str,
):
    dialog_manager.dialog_data[DATA_CURRENT_NOMINATION_ID] = item_id
    await dialog_manager.find(ID_VOTING_SCROLL).set_page(0)
    await dialog_manager.switch_to(states.VOTING.VOTING)


async def add_vote_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    app: AppHolder = dialog_manager.middleware_data["app"]
    try:
        await app.voting.add_vote(
            user_id=dialog_manager.event.from_user.id,
            participant_id=data,
            nomination_id=dialog_manager.dialog_data[DATA_CURRENT_NOMINATION_ID],
        )
    except ServiceError as e:
        await message.reply(e.message)
        return


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


nominations_window = Window(
    Title(Const(strings.titles.voting)),
    Const("Для голосования доступны следующие номинации"),
    Column(
        Select(
            Format("{item[1]}"),
            id="nomination",
            item_id_getter=operator.itemgetter(0),
            items="nominations_list",
            type_factory=str,
            on_click=select_nomination_handler,
        ),
    ),
    StubScroll(ID_NOMINATIONS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_NOMINATIONS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("⏭️")),
        when=F["pages"] > 1,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.VOTING.SELECT_NOMINATION,
    getter=nominations_getter,
)

voting_window = Window(
    Title(Format("🎖️ Номинация {nomination_title}")),
    Jinja(voting_list),
    Const("⌨️ Чтобы проголосовать, отправь номер участника.", when=~F["voted"]),
    StubScroll(ID_VOTING_SCROLL, pages="pages"),
    Row(
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
        type_factory=int,
        on_success=add_vote_handler,
    ),
    Button(
        Const("🗑️ Отменить голос"),
        id="cancel_vote",
        when="voted",
        on_click=cancel_vote_handler,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.VOTING.SELECT_NOMINATION,
        id="nominations",
    ),
    state=states.VOTING.VOTING,
    getter=participants_getter,
)


dialog = Dialog(nominations_window, voting_window)
