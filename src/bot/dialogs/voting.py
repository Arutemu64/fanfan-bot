import operator
from typing import Any, TypedDict

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

ID_NOMINATIONS_SCROLL = "nominations_scroll"
ID_VOTING_SCROLL = "voting_scroll"


class UserVoteData(TypedDict):
    id: int
    participant_id: int


with open(TEMPLATES_DIR / "voting.jinja2", "r", encoding="utf-8") as file:
    VotingList = Jinja(file.read())


async def nominations_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    page = await db.nomination.paginate(
        page=await dialog_manager.find(ID_NOMINATIONS_SCROLL).get_page(),
        nominations_per_page=dialog_manager.dialog_data["items_per_page"],
        votable=True,
    )
    voted_nominations = await db.vote.check_list_of_user_voted_nominations(
        user_id=dialog_manager.event.from_user.id,
        nomination_ids=[n.id for n in page.items],
    )
    nominations_list = []
    for nomination in page.items:
        if nomination.id in voted_nominations:
            nomination.title = nomination.title + " ✅"
        nominations_list.append((nomination.id, nomination.title))
    dialog_manager.dialog_data["vote"] = None
    return {
        "pages": page.total,
        "nominations_list": nominations_list,
    }


async def participants_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    nomination_id = dialog_manager.dialog_data["nomination_id"]
    nomination = await db.nomination.get(nomination_id)
    page = await db.participant.paginate(
        page=await dialog_manager.find(ID_VOTING_SCROLL).get_page(),
        participants_per_page=dialog_manager.dialog_data["items_per_page"],
        nomination_id=nomination_id,
        event_skip=False,
        load_votes_count=True,
    )
    return {
        "pages": page.total,
        "nomination_title": nomination.title,
        "participants": page.items,
        "vote": dialog_manager.dialog_data["vote"],
    }


async def select_nomination(
    callback: CallbackQuery, widget: Any, dialog_manager: DialogManager, item_id: str
):
    db: Database = dialog_manager.middleware_data["db"]
    dialog_manager.dialog_data["nomination_id"] = item_id
    user_vote = await db.vote.get_user_vote(
        user_id=dialog_manager.event.from_user.id, nomination_id=item_id
    )
    if user_vote:
        dialog_manager.dialog_data["vote"]: UserVoteData = {
            "id": user_vote.id,
            "participant_id": user_vote.participant_id,
        }
    else:
        dialog_manager.dialog_data["vote"] = None
    await dialog_manager.find(ID_VOTING_SCROLL).set_page(0)
    await dialog_manager.switch_to(states.VOTING.VOTING)


async def add_vote(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: int,
):
    db: Database = dialog_manager.middleware_data["db"]

    if dialog_manager.dialog_data.get("vote"):
        await message.reply("⚠️ Вы уже голосовали в этой категории!")
        return
    if not await db.settings.get_voting_enabled():
        await message.reply(strings.errors.voting_disabled)
        return
    if await db.participant.exists(data):
        user_vote = await db.vote.new(message.from_user.id, data)
        await db.session.commit()
        dialog_manager.dialog_data["vote"]: UserVoteData = {
            "id": user_vote.id,
            "participant_id": user_vote.participant_id,
        }
    else:
        await message.reply("⚠️ Неверно указан номер участника")
        return


async def cancel_vote(callback: CallbackQuery, button: Button, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    if not await db.settings.get_voting_enabled():
        await callback.answer(strings.errors.voting_disabled)
        return
    await db.vote.delete(manager.dialog_data["vote"]["id"])
    await db.session.commit()
    manager.dialog_data["vote"] = None


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
        when="vote",
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


async def on_voting_start(start_data: Any, manager: DialogManager):
    db: Database = manager.middleware_data["db"]
    user = await db.user.get(manager.event.from_user.id)
    manager.dialog_data["items_per_page"] = user.items_per_page


dialog = Dialog(nominations, voting, on_start=on_voting_start)
