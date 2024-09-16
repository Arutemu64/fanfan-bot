from dishka import Provider, Scope, provide

from fanfan.application.achievements.add_achievement_to_user import AddAchievementToUser
from fanfan.application.achievements.get_achievement_by_secret_id import (
    GetAchievementBySecretId,
)
from fanfan.application.achievements.get_achievements_page import GetAchievementsPage
from fanfan.application.activities.get_activities_page import GetActivitiesPage
from fanfan.application.activities.get_activity_by_id import GetActivityById
from fanfan.application.events.get_current_event import GetCurrentEvent
from fanfan.application.events.get_event_by_id import GetEventById
from fanfan.application.events.get_page_number_by_event import GetPageNumberByEvent
from fanfan.application.events.get_schedule_page import GetSchedulePage
from fanfan.application.events.move_event import MoveEvent
from fanfan.application.events.set_current_event import SetCurrentEvent
from fanfan.application.events.set_next_event import SetNextEvent
from fanfan.application.events.skip_event import SkipEvent
from fanfan.application.feedback.send_feedback import SendFeedback
from fanfan.application.mailing.create_mailing import CreateMailing
from fanfan.application.mailing.delete_mailing import DeleteMailing
from fanfan.application.nominations.get_nomination_by_id import GetNominationById
from fanfan.application.nominations.get_nominations_page import GetNominationsPage
from fanfan.application.other.get_random_quote import GetRandomQuote
from fanfan.application.participants.get_participant_by_scoped_id import (
    GetParticipantByScopedId,
)
from fanfan.application.participants.get_participants_page import GetParticipantsPage
from fanfan.application.quest.get_user_stats import GetUserStats
from fanfan.application.settings.get_settings import GetSettings
from fanfan.application.settings.update_settings import UpdateSettings
from fanfan.application.subscriptions.create_subscription import CreateSubscription
from fanfan.application.subscriptions.delete_subscription import DeleteSubscription
from fanfan.application.subscriptions.get_subscription_by_event import (
    GetSubscriptionByEvent,
)
from fanfan.application.subscriptions.get_subscriptions_page import GetSubscriptionsPage
from fanfan.application.tickets.create_ticket import CreateTicket
from fanfan.application.tickets.delete_ticket import DeleteTicket
from fanfan.application.tickets.link_ticket import LinkTicket
from fanfan.application.users.create_user import CreateUser
from fanfan.application.users.find_user_by_username import FindUserByUsername
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.application.users.update_user import UpdateUser
from fanfan.application.users.update_user_commands import UpdateUserCommands
from fanfan.application.votes.add_vote import AddVote
from fanfan.application.votes.cancel_vote import CancelVote


class InteractorsProvider(Provider):
    scope = Scope.REQUEST

    get_achievement_by_secret_id = provide(GetAchievementBySecretId)
    get_achievements_page = provide(GetAchievementsPage)
    receive_achievement = provide(AddAchievementToUser)

    get_activities_page = provide(GetActivitiesPage)
    get_activity_by_id = provide(GetActivityById)

    get_random_quote = provide(GetRandomQuote)

    get_current_event = provide(GetCurrentEvent)
    get_event_by_id = provide(GetEventById)
    get_page_number_by_event = provide(GetPageNumberByEvent)
    get_schedule_page = provide(GetSchedulePage)
    move_event = provide(MoveEvent)
    set_current_event = provide(SetCurrentEvent)
    set_next_event = provide(SetNextEvent)
    skip_event = provide(SkipEvent)

    send_feedback = provide(SendFeedback)

    create_mailing = provide(CreateMailing)
    delete_mailing = provide(DeleteMailing)

    get_nomination_by_id = provide(GetNominationById)
    get_nominations_page = provide(GetNominationsPage)

    get_participant_by_scoped_id = provide(GetParticipantByScopedId)
    get_participants_page = provide(GetParticipantsPage)

    get_settings = provide(GetSettings)
    update_settings = provide(UpdateSettings)

    create_subscription = provide(CreateSubscription)
    delete_subscription = provide(DeleteSubscription)
    get_subscription_by_event = provide(GetSubscriptionByEvent)
    get_subscriptions_page = provide(GetSubscriptionsPage)

    create_ticket = provide(CreateTicket)
    delete_ticket = provide(DeleteTicket)
    link_ticket = provide(LinkTicket)

    create_user = provide(CreateUser)
    get_user_by_id = provide(GetUserById)
    get_user_by_username = provide(FindUserByUsername)
    get_user_stats = provide(GetUserStats)
    update_user = provide(UpdateUser)
    update_user_commands = provide(UpdateUserCommands)

    add_vote = provide(AddVote)
    cancel_vote = provide(CancelVote)
