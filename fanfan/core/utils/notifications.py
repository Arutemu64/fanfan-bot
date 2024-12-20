import html

from aiogram.utils.keyboard import InlineKeyboardBuilder

from fanfan.core.models.achievement import Achievement
from fanfan.core.models.feedback import FullFeedback
from fanfan.core.models.notification import DEFAULT_REPLY_MARKUP, UserNotification
from fanfan.core.utils.pluralize import Plurals, pluralize
from fanfan.presentation.tgbot.keyboards.buttons import (
    DELETE_BUTTON,
    PULL_DOWN_DIALOG,
    process_feedback_button,
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


def create_feedback_notification(feedback: FullFeedback) -> UserNotification:
    if feedback.processed_by is None:
        bottom_text = (
            "🙋 Нажмите кнопку, если готовы взять обработку отзыва на себя\n"
            "⚙️ Уведомления можно отключить в настройках\n"
            "⚠️ Пользователю можно ограничить доступ к обратной связи, "
            "отозвав разрешение can_send_feedback"
        )
        reply_markup = InlineKeyboardBuilder(
            [
                [process_feedback_button(feedback_id=feedback.id)],
                [PULL_DOWN_DIALOG],
            ]
        ).as_markup()
    else:
        bottom_text = f"✅ @{feedback.processed_by.username} взял отзыв в работу"
        reply_markup = DEFAULT_REPLY_MARKUP
    return UserNotification(
        title="💬 ОБРАТНАЯ СВЯЗЬ",
        text=f"Поступила обратная связь "
        f"от @{feedback.user.username} ({feedback.user_id}):\n\n"
        f"<blockquote>{html.escape(feedback.text)}</blockquote>",
        bottom_text=bottom_text,
        reply_markup=reply_markup,
    )


def create_error_notification(exception: Exception) -> UserNotification:
    return UserNotification(
        title="⚠️ НЕИЗВЕСТНАЯ ОШИБКА",
        text=f"Возникла необработанная ошибка ({type(exception).__name__}). "
        f"Мы постараемся исправить проблему в ближайшее время, а пока "
        f"можешь попробовать перезапустить бота командой /start "
        f"и попробовать ещё раз",
        reply_markup=InlineKeyboardBuilder([[DELETE_BUTTON]]).as_markup(),
    )
