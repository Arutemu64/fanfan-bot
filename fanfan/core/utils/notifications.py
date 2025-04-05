import html

from aiogram.utils.keyboard import InlineKeyboardBuilder

from fanfan.core.dto.notification import UserNotification
from fanfan.core.exceptions.base import AppException
from fanfan.core.models.achievement import Achievement
from fanfan.core.models.feedback import FeedbackFull
from fanfan.core.utils.pluralize import Plurals, pluralize
from fanfan.presentation.tgbot.keyboards.buttons import (
    DELETE_BUTTON,
    PULL_DOWN_DIALOG,
    process_feedback_button,
    show_user_info_button,
)


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


def create_feedback_notification(feedback: FeedbackFull) -> UserNotification:
    bottom_text = (
        "⚙️ Уведомления можно отключить в личных настройках.\n"
        "⚠️ Пользователю можно ограничить доступ к обратной связи, "
        "отозвав разрешение can_send_feedback через орг-панель.\n"
    )
    if feedback.processed_by is None:
        bottom_text += "🙋 Нажмите кнопку, если готовы взять обработку отзыва на себя."
        reply_markup = InlineKeyboardBuilder(
            [
                [process_feedback_button(feedback_id=feedback.id)],
                [show_user_info_button(user_id=feedback.user_id)],
                [PULL_DOWN_DIALOG],
            ]
        ).as_markup()
    else:
        bottom_text += f"✅ @{feedback.processed_by.username} взял отзыв в работу."
        reply_markup = InlineKeyboardBuilder(
            [
                [show_user_info_button(user_id=feedback.user_id)],
                [PULL_DOWN_DIALOG],
            ]
        ).as_markup()
    return UserNotification(
        title="💬 ОБРАТНАЯ СВЯЗЬ",
        text=f"Поступила обратная связь "
        f"от @{feedback.user.username} ({feedback.user_id}):\n\n"
        f"<blockquote>{html.escape(feedback.text)}</blockquote>",
        bottom_text=bottom_text,
        reply_markup=reply_markup,
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
        text=f"Возникла необработанная ошибка ({type(exception).__name__}). "
        f"Мы постараемся исправить проблему в ближайшее время, а пока "
        f"можешь попробовать перезапустить бота командой /start "
        f"и попробовать ещё раз",
        reply_markup=InlineKeyboardBuilder([[DELETE_BUTTON]]).as_markup(),
    )
