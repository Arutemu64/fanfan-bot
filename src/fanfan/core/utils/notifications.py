from aiogram.utils.keyboard import InlineKeyboardBuilder

from fanfan.core.dto.notification import UserNotification
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.achievement import Achievement
from fanfan.core.utils.pluralize import Plurals, pluralize
from fanfan.presentation.tgbot.keyboards.buttons import DELETE_BUTTON


def create_achievement_notification(achievement: Achievement) -> UserNotification:
    return UserNotification(
        title="🏆 Новое достижение",
        text=f"Ты получил новое достижение <b>{achievement.title}</b>",
    )


def create_points_notification(points: int, comment: str | None) -> UserNotification:
    points_pluralized = pluralize(points, Plurals("очко", "очка", "очков"))
    text = f"Ты заработал <b>{points} {points_pluralized}</b>"
    if comment:
        text += f"\n\n<blockquote>{comment}</blockquote>"
    return UserNotification(
        title="💰 Ты заработал очки",
        text=text,
    )


def create_app_exception_notification(app_exception: AppException) -> UserNotification:
    return UserNotification(
        title="⚠️ ОШИБКА",
        text=app_exception.message,
        reply_markup=InlineKeyboardBuilder([[DELETE_BUTTON]]).as_markup(),
    )


def create_exception_notification(exception: Exception) -> UserNotification:
    return UserNotification(
        title="⚠️ НЕИЗВЕСТНАЯ ОШИБКА",
        text=f"Возникла неизвестная ошибка ({type(exception).__name__}). "
        f"Мы постараемся исправить проблему в ближайшее время, а пока "
        f"можешь попробовать перезапустить бота командой /start "
        f"и попробовать ещё раз, это может помочь.",
        reply_markup=InlineKeyboardBuilder([[DELETE_BUTTON]]).as_markup(),
    )
