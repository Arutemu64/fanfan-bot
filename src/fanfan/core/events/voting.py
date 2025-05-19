from dataclasses import dataclass

from fanfan.core.events.base import AppEvent
from fanfan.core.models.vote import Vote


@dataclass(kw_only=True, slots=True)
class VoteUpdatedEvent(AppEvent):
    subject: str = "vote.updated"

    vote: Vote
