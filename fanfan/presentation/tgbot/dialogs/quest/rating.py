import typing

from aiogram import F
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import (
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
from dishka import AsyncContainer

from fanfan.application.quest.get_quest_rating import GetQuestRating, GetQuestRatingDTO
from fanfan.core.dto.page import Pagination
from fanfan.core.models.user import UserData
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings
from fanfan.presentation.tgbot.templates import rating_list

if typing.TYPE_CHECKING:
    from aiogram_dialog.widgets.common import ManagedScroll

ID_RATING_SCROLL = "rating_scroll"


async def rating_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: UserData,
    **kwargs,
) -> dict:
    scroll: ManagedScroll = dialog_manager.find(ID_RATING_SCROLL)
    get_quest_rating: GetQuestRating = await container.get(GetQuestRating)
    rating = await get_quest_rating(
        GetQuestRatingDTO(
            pagination=Pagination(
                limit=user.settings.items_per_page,
                offset=await scroll.get_page() * user.settings.items_per_page,
            )
        )
    )
    return {
        "players": rating.items,
        "pages": rating.total // user.settings.items_per_page
        + bool(rating.total % user.settings.items_per_page),
    }


rating_window = Window(
    Title(Const(strings.titles.rating)),
    Jinja(rating_list),
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
        when=F["pages"] > 1,
    ),
    SwitchTo(Const(strings.buttons.back), state=states.Quest.MAIN, id="back"),
    getter=rating_getter,
    state=states.Quest.RATING,
)
