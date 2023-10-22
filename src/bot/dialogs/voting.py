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

from src.bot import TEMPLATES_DIR
from src.bot.dialogs import states
from src.bot.dialogs.widgets import FormatTitle, Title
from src.bot.ui import strings
from src.db import Database
from src.db.models import User

ID_NOMINATIONS_SCROLL = "nominations_scroll"
ID_VOTING_SCROLL = "voting_scroll"


with open(TEMPLATES_DIR / "voting.jinja2", "r", encoding="utf-8") as file:
    VotingList = Jinja(file.read())


async def nominations_getter(
    dialog_manager: DialogManager, db: Database, current_user: User, **kwargs
):
    page = await db.nomination.paginate(
        page=await dialog_manager.find(ID_NOMINATIONS_SCROLL).get_page(),
        nominations_per_page=current_user.items_per_page,
        votable=True,
    )
    voted_nominations = await db.nomination.get_user_voted_nominations(current_user)
    nominations_list = []
    for nomination in page.items:
        if nomination in voted_nominations:
            nomination.title = nomination.title + " ✅"
        nominations_list.append((nomination.id, nomination.title))
    return {
        "pages": page.total,
        "nominations_list": nominations_list,
    }


async def participants_getter(
    dialog_manager: DialogManager, db: Database, current_user: User, **kwargs
):
    nomination = await db.nomination.get(dialog_manager.dialog_data["nomination_id"])
    page = await db.participant.paginate(
        page=await dialog_manager.find(ID_VOTING_SCROLL).get_page(),
        participants_per_page=current_user.items_per_page,
        nomination=nomination,
        hide_event_skip=True,
    )
    user_vote = await db.vote.get_user_vote_by_nomination(current_user, nomination)
    dialog_manager.dialog_data["user_vote_id"] = user_vote.id if user_vote else None
    return {
        "nomination_title": nomination.title,
        "pages": page.total,
        "participants": page.items,
        "user_vote": user_vote,
    }


async def select_nomination(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    dialog_manager.dialog_data["nomination_id"] = item_id
    await dialog_manager.find(ID_VOTING_SCROLL).set_page(0)
    await dialog_manager.switch_to(states.VOTING.VOTING)


async def add_vote(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]
    user: User = dialog_manager.middleware_data["current_user"]

    if dialog_manager.dialog_data["user_vote_id"]:
        await message.reply("⚠️ Вы уже голосовали в этой категории!")
        return
    if not await db.settings.get_voting_enabled():
        await message.reply(strings.errors.voting_disabled)
        return
    nomination = await db.nomination.get(dialog_manager.dialog_data["nomination_id"])
    participant = await db.participant.get_for_vote(data, nomination)
    if participant:
        await db.vote.new(user, participant)
        await db.session.commit()
    else:
        await message.reply("⚠️ Неверно указан номер участника")


async def cancel_vote(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    if not await db.settings.get_voting_enabled():
        await callback.answer(strings.errors.voting_disabled)
        return
    user_vote = await db.vote.get(manager.dialog_data["user_vote_id"])
    await db.session.delete(user_vote)
    await db.session.commit()


nominations = Window(
    Title(strings.titles.voting),
    Const("Для голосования доступны следующие номинации"),
    Column(
        Select(
            Format("{item[1]}"),
            id="nomination",
            item_id_getter=operator.itemgetter(0),
            items="nominations_list",
            type_factory=str,
            on_click=select_nomination,
        ),
    ),
    StubScroll(ID_NOMINATIONS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_NOMINATIONS_SCROLL, text=Format(text="{current_page1}/{pages}")
        ),
        NextPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_NOMINATIONS_SCROLL, text=Const("⏭️")),
        when=F["pages"] != 1,
    ),
    Cancel(Const(strings.buttons.back)),
    state=states.VOTING.NOMINATIONS,
    getter=nominations_getter,
)

voting = Window(
    FormatTitle("🎖️ Номинация {nomination_title}"),
    VotingList,
    Const("⌨️ Чтобы проголосовать, отправь номер участника.", when=~F["user_vote"]),
    StubScroll(ID_VOTING_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_VOTING_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_VOTING_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_VOTING_SCROLL, text=Format(text="{current_page1}/{pages}")
        ),
        NextPage(scroll=ID_VOTING_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_VOTING_SCROLL, text=Const("⏭️")),
        when=F["pages"] != 1,
    ),
    TextInput(
        id="vote_id_input",
        type_factory=int,
        on_success=add_vote,
    ),
    Button(
        Const("Отменить голос"),
        id="cancel_vote",
        when="user_vote",
        on_click=cancel_vote,
    ),
    SwitchTo(
        text=Const(strings.buttons.back),
        state=states.VOTING.NOMINATIONS,
        id="nominations",
    ),
    state=states.VOTING.VOTING,
    getter=participants_getter,
)


dialog = Dialog(nominations, voting)
