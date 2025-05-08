from dataclasses import dataclass

from fanfan.core.events.base import AppEvent
from fanfan.core.models.feedback import FeedbackId


@dataclass(kw_only=True, slots=True)
class NewFeedbackEvent(AppEvent):
    subject: str = "feedback.new"

    feedback_id: FeedbackId


@dataclass(kw_only=True, slots=True)
class FeedbackProcessedEvent(AppEvent):
    subject: str = "feedback.processed"

    feedback_id: FeedbackId
