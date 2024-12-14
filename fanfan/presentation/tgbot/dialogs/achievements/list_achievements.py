from aiogram import F
from aiogram.types import Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Cancel,
    CurrentPage,
    FirstPage,
    LastPage,
    NextPage,
    PrevPage,
    Row,
    StubScroll,
)
from aiogram_dialog.widgets.text import Case, Const, Format, Jinja
from dishka import AsyncContainer
from dishka.integrations.aiogram import CONTAINER_NAME

from fanfan.application.quest.add_achievement import (
    AddAchievement,
    AddAchievementDTO,
)
from fanfan.application.quest.get_achievements_page import GetAchievementsPage
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.core.dto.page import Pagination
from fanfan.core.exceptions.achievements import UserAlreadyHasThisAchievement
from fanfan.core.exceptions.users import TicketNotLinked
from fanfan.core.models.achievement import AchievementId
from fanfan.core.models.user import FullUser, UserId
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static.templates import achievements_list
from fanfan.presentation.tgbot.ui import strings

ID_ACHIEVEMENTS_SCROLL = "achievements_scroll"
ID_ADD_ACHIEVEMENT_INPUT = "add_achievement_input"
DATA_USER_ID = "user_id"


async def list_achievements_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    user: FullUser,
    **kwargs,
) -> dict:
    get_achievements_page: GetAchievementsPage = await container.get(
        GetAchievementsPage
    )

    page = await get_achievements_page(
        pagination=Pagination(
            limit=user.settings.items_per_page,
            offset=await dialog_manager.find(ID_ACHIEVEMENTS_SCROLL).get_page()
            * user.settings.items_per_page,
        ),
        for_user_id=dialog_manager.start_data[DATA_USER_ID],
    )

    showing_self = dialog_manager.start_data[DATA_USER_ID] == user.id
    if showing_self:
        username = user.username
    else:
        get_user_by_id: GetUserById = await container.get(GetUserById)
        username = (
            await get_user_by_id(dialog_manager.start_data[DATA_USER_ID])
        ).username

    return {
        "achievements": page.items,
        "pages": page.total // user.settings.items_per_page
        + bool(page.total % user.settings.items_per_page),
        "showing_self": showing_self,
        "username": username,
        "add_mode": bool(dialog_manager.start_data.get("add_mode")),
    }


async def add_achievement_to_user_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    container: AsyncContainer = dialog_manager.middleware_data[CONTAINER_NAME]

    if (
        "/" in data
        and data.replace("/", "").isnumeric()
        and bool(dialog_manager.start_data.get("add_mode"))
    ):
        try:
            add_achievement: AddAchievement = await container.get(AddAchievement)
            await add_achievement(
                AddAchievementDTO(
                    achievement_id=AchievementId(int(data.replace("/", ""))),
                    to_user_id=UserId(dialog_manager.start_data[DATA_USER_ID]),
                )
            )
        except TicketNotLinked:
            await message.answer("⚠️ У участника не привязан билет")
            return
        except UserAlreadyHasThisAchievement:
            await message.answer("⚠️ У участника уже есть это достижение")
            return


list_achievements_window = Window(
    Title(
        Case(
            texts={
                True: Const("🏆 Твои достижения"),
                False: Format("🏆 Достижения @{username}"),
            },
            selector="showing_self",
        ),
    ),
    Jinja(achievements_list),
    StubScroll(id=ID_ACHIEVEMENTS_SCROLL, pages="pages"),
    Row(
        FirstPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("⏪")),
        PrevPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("◀️")),
        CurrentPage(
            scroll=ID_ACHIEVEMENTS_SCROLL,
            text=Format(text="{current_page1}/{pages}"),
        ),
        NextPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("▶️")),
        LastPage(scroll=ID_ACHIEVEMENTS_SCROLL, text=Const("⏭️")),
        when=F["pages"] > 1,
    ),
    TextInput(
        id=ID_ADD_ACHIEVEMENT_INPUT,
        type_factory=str,
        on_success=add_achievement_to_user_handler,
    ),
    Cancel(text=Const(strings.buttons.back)),
    state=states.Achievements.list_achievements,
    getter=list_achievements_getter,
)
