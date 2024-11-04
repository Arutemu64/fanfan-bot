import html

from aiogram.utils.keyboard import InlineKeyboardBuilder

from fanfan.core.models.achievement import AchievementModel
from fanfan.core.models.feedback import FullFeedbackModel
from fanfan.core.models.notification import DEFAULT_REPLY_MARKUP, UserNotification
from fanfan.presentation.tgbot.keyboards.buttons import (
    PULL_DOWN_DIALOG,
    process_feedback_button,
)


def create_achievement_notification(achievement: AchievementModel) -> UserNotification:
    return UserNotification(
        title="🏆 Новое достижение",
        text=f"Ты получил новое достижение <b>{achievement.title}</b>",
    )


def create_points_notification(points: int) -> UserNotification:
    return UserNotification(
        title="🤑 Денежки пришли", text=f"Ты заработал <b>{points} очков</b>"
    )


def create_feedback_notification(feedback: FullFeedbackModel) -> UserNotification:
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
