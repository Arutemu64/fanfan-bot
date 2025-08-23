from .achievement import AchievementView
from .activity import ActivityView
from .code import CodeView
from .event import EventView
from .feedback import FeedbackView
from .nomination import NominationView
from .participant import ParticipantView
from .quote import QuoteView
from .ticket import TicketView
from .transaction import TransactionView
from .user import UserSettingsView, UserView
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
    UserSettingsView,
    VoteView,
    FeedbackView,
    TransactionView,
    CodeView,
]
