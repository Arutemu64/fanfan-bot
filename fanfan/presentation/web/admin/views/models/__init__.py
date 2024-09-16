from .achievement import AchievementView
from .activity import ActivityView
from .event import EventView
from .feedback import FeedbackView
from .nomination import NominationView
from .participant import ParticipantView
from .quote import QuoteView
from .ticket import TicketView
from .user import UserPermissionsView, UserSettingsView, UserView
from .vote import VoteView

model_views = [
    AchievementView,
    ActivityView,
    EventView,
    NominationView,
    ParticipantView,
    QuoteView,
    TicketView,
    UserView,
    UserPermissionsView,
    UserSettingsView,
    VoteView,
    FeedbackView,
]
