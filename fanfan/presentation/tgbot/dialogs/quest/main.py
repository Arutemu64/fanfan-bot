import math

from aiogram import F
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, Cancel, Group, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Multi, Progress
from dishka import AsyncContainer

from fanfan.application.quest.get_quest_conditions import GetQuestConditions
from fanfan.application.quest.get_user_quest_details import GetUserQuestStats
from fanfan.application.quest.register_to_quest import RegisterToQuest
from fanfan.common import QR_CODES_TEMP_DIR
from fanfan.core.dto.qr import QR, QRType
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.user import FullUserModel
from fanfan.core.utils.qr import generate_img
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.achievements import start_achievements
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings


async def quest_main_getter(
    dialog_manager: DialogManager,
    user: FullUserModel,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    get_user_stats: GetUserQuestStats = await container.get(GetUserQuestStats)
    get_quest_conditions: GetQuestConditions = await container.get(GetQuestConditions)

    achievements_progress = 0
    user_stats = await get_user_stats(user.id)
    if user_stats.total_achievements > 0:
        achievements_progress = math.floor(
            user_stats.achievements_count * 100 / user_stats.total_achievements,
        )

    quest_conditions = await get_quest_conditions()

    qr = QR(type=QRType.USER, data=str(user.id))
    qr_file_path = QR_CODES_TEMP_DIR.joinpath(f"{hash(qr)}.png")
    if not qr_file_path.is_file():
        generate_img(qr).save(qr_file_path)

    return {
        # Quest conditions
        "is_registration_open": quest_conditions.is_registration_open,
        "can_user_participate": quest_conditions.can_user_participate,
        # User stats
        "points": user_stats.points,
        "achievements_count": user_stats.achievements_count,
        "achievements_progress": achievements_progress,
        "total_achievements": user_stats.total_achievements,
        "quest_registration": user_stats.quest_registration,
        # QR
        "qr_file_path": qr_file_path,
    }


async def open_achievements_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    await start_achievements(manager, manager.event.from_user.id)
    return


async def register_to_quest_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    register: RegisterToQuest = await container.get(RegisterToQuest)

    try:
        await register()
    except AppException as e:
        await callback.answer(e.message, show_alert=True)
        return


main_quest_window = Window(
    StaticMedia(path=Format("{qr_file_path}")),
    Title(Const(strings.titles.quest)),
    Const(
        "Во время фестиваля можно поучаствовать в разнообразных активностях "
        "и проверить глубину своего познания мира фантастики и анимации! "
    ),
    Const(" "),
    Multi(
        Format("<b>💰 Очков:</b> {points}"),
        Format("<b>🏆 Достижений:</b> {achievements_count} из {total_achievements}"),
        Progress(field="achievements_progress", filled="🟩", empty="⬜"),
        Const(" "),
        Const(
            "✅ Ты зарегистрирован в квесте, удачи!",
            when=F["quest_registration"],
        ),
        Multi(
            Const(
                "✅ Регистрация на квест открыта, "
                "не забудь её пройти, чтобы побороться за призы!",
                when=F["is_registration_open"],
            ),
            Const(
                "⛔ К сожалению, регистрация на квест сейчас закрыта, попробуй позже.\n"
                "Но ты можешь участвовать в некоторых активностях и без неё!",
                when=~F["is_registration_open"],
            ),
            when=~F["quest_registration"],
        ),
    ),
    Group(
        Button(
            text=Const("📃 Зарегистрироваться на квест"),
            id="register_to_quest",
            on_click=register_to_quest_handler,
            when=~F["quest_registration"] & F["is_registration_open"],
        ),
        SwitchTo(
            text=Const("🗑️ Отменить регистрацию"),
            id="unregister_from_quest",
            state=states.Quest.cancel_registration,
            when=F["quest_registration"],
        ),
        Button(
            text=Const("🏆 Мои достижения"),
            id="open_achievements",
            on_click=open_achievements_handler,
        ),
        when=F["can_user_participate"],
    ),
    Cancel(Const(strings.buttons.back)),
    getter=quest_main_getter,
    state=states.Quest.main,
)
