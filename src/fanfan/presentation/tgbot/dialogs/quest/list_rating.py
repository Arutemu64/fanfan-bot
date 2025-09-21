import typing

from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
    Button,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
    SwitchTo,
)
from aiogram_dialog.widgets.text import Const, Format, Jinja
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject

from fanfan.application.quest.get_quest_rating import GetQuestRating, GetQuestRatingDTO
from fanfan.core.dto.page import Pagination
from fanfan.core.dto.user import FullUserDTO
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.utils import get_current_user
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import rating_list

if typing.TYPE_CHECKING:
    from aiogram_dialog.widgets.common import ManagedScroll

ID_RATING_SCROLL = "rating_scroll"


@inject
async def rating_getter(
    dialog_manager: DialogManager,
    current_user: FullUserDTO,
    get_quest_rating: FromDishka[GetQuestRating],
    **kwargs,
) -> dict:
    scroll: ManagedScroll = dialog_manager.find(ID_RATING_SCROLL)
    rating = await get_quest_rating(
        GetQuestRatingDTO(
            pagination=Pagination(
                limit=current_user.settings.items_per_page,
                offset=await scroll.get_page() * current_user.settings.items_per_page,
            )
        )
    )
    pages = rating.total // current_user.settings.items_per_page + bool(
        rating.total % current_user.settings.items_per_page
    )
    return {
        "players": rating.items,
        "pages": pages or 1,
        "current_user_id": current_user.id,
    }


@inject
async def find_me_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
    get_quest_rating: FromDishka[GetQuestRating],
) -> None:
    scroll: ManagedScroll = manager.find(ID_RATING_SCROLL)
    current_user = get_current_user(manager)

    rating = await get_quest_rating(GetQuestRatingDTO())
    page = None
    for idx, player in enumerate(rating.items):
        if player.user_id == current_user.id:
            page = idx // current_user.settings.items_per_page

    if page is not None:
        await scroll.set_page(page)
    else:
        await callback.answer("😢 Не нашли тебя в рейтинге")


rating_window = Window(
    Title(Const(strings.titles.rating)),
    Jinja(rating_list),
    Const("⌛ Рейтинг обновляется раз в минуту"),
    Button(
        Const("🔍 Где я?"),
        id="find_me_button",
        on_click=find_me_handler,
    ),
    Row(
        StubScroll(ID_RATING_SCROLL, pages="pages"),
        FirstPage(scroll=ID_RATING_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_RATING_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_RATING_SCROLL,
            text=Format(text="{current_page1}/{pages} 🔄️"),
        ),
        NextPage(scroll=ID_RATING_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_RATING_SCROLL, text=Const("⏭️")),
    ),
    SwitchTo(Const(strings.buttons.back), state=states.Quest.MAIN, id="back"),
    getter=rating_getter,
    state=states.Quest.RATING,
)
