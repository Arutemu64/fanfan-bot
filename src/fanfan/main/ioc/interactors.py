from dishka import Provider, Scope, provide

from fanfan.application.activities.get_activities_page import GetActivitiesPage
from fanfan.application.activities.get_activity_by_id import GetActivityById
from fanfan.application.codes.get_code_by_id import GetCodeById
from fanfan.application.codes.get_user_code_id import GetUserCodeId
from fanfan.application.etc.get_random_quote import GetRandomQuote
from fanfan.application.mailing.cancel_mailing import CancelMailing
from fanfan.application.mailing.create_role_mailing import CreateRoleMailing
from fanfan.application.mailing.get_mailing_info import GetMailingInfo
from fanfan.application.mailing.send_message_to_user import SendMessageToUser
from fanfan.application.marketplace.create_market_by_participant import (
    CreateMarketByParticipant,
)
from fanfan.application.marketplace.create_product import CreateProduct
from fanfan.application.marketplace.get_market_by_id import GetMarketById
from fanfan.application.marketplace.get_markets_page import GetMarketsPage
from fanfan.application.marketplace.get_product_by_id import GetProductById
from fanfan.application.marketplace.get_products_page import GetProductsPage
from fanfan.application.marketplace.update_market import UpdateMarket
from fanfan.application.marketplace.update_product import UpdateProduct
from fanfan.application.quest.add_points_to_user import AddPointsToUser
from fanfan.application.quest.get_achievements_page import (
    GetAchievementsPage,
)
from fanfan.application.quest.get_quest_rating import GetQuestRating
from fanfan.application.quest.get_user_quest_status import GetUserQuestStatus
from fanfan.application.quest.receive_achievement import ReceiveAchievement
from fanfan.application.quest.reset_quest import ResetQuest
from fanfan.application.schedule.get_schedule import (
    GetSchedulePage,
)
from fanfan.application.schedule.get_schedule_event_by_id import GetScheduleEventById
from fanfan.application.schedule.management.move_event import MoveScheduleEvent
from fanfan.application.schedule.management.replace_schedule import ReplaceSchedule
from fanfan.application.schedule.management.revert_change import RevertScheduleChange
from fanfan.application.schedule.management.set_current_event import (
    SetCurrentScheduleEvent,
)
from fanfan.application.schedule.management.set_next_event import SetNextScheduleEvent
from fanfan.application.schedule.management.skip_event import SkipScheduleEvent
from fanfan.application.schedule.subscriptions.create_subscription import (
    CreateSubscription,
)
from fanfan.application.schedule.subscriptions.delete_subscription import (
    DeleteSubscription,
)
from fanfan.application.schedule.subscriptions.get_subscriptions_page import (
    GetSubscriptionsPage,
)
from fanfan.application.settings.get_settings import GetSettings
from fanfan.application.settings.update_settings import UpdateSettings
from fanfan.application.tickets.delete_ticket import DeleteTicket
from fanfan.application.tickets.generate_ticket import GenerateTicket
from fanfan.application.tickets.link_ticket import LinkTicket
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.application.users.get_user_by_username import GetUserByUsername
from fanfan.application.users.tg_authenticate import TgAuthenticate
from fanfan.application.users.update_user import UpdateUser
from fanfan.application.users.update_user_settings import UpdateUserSettings
from fanfan.application.voting.add_vote import AddVote
from fanfan.application.voting.cancel_vote import CancelVote
from fanfan.application.voting.get_nomination_by_id import GetNominationById
from fanfan.application.voting.get_nominations_page import (
    GetNominationsPage,
)
from fanfan.application.voting.get_participants_page import (
    GetParticipantsPage,
)
from fanfan.application.voting.get_voting_state import GetVotingState


class InteractorsProvider(Provider):
    scope = Scope.REQUEST

    get_achievements_page = provide(GetAchievementsPage)

    get_activities_page = provide(GetActivitiesPage)
    get_activity_by_id = provide(GetActivityById)

    get_random_quote = provide(GetRandomQuote)

    get_event_by_id = provide(GetScheduleEventById)
    get_schedule_page = provide(GetSchedulePage)

    move_event = provide(MoveScheduleEvent)
    set_current_event = provide(SetCurrentScheduleEvent)
    set_next_event = provide(SetNextScheduleEvent)
    skip_event = provide(SkipScheduleEvent)
    revert_change = provide(RevertScheduleChange)
    replace_schedule = provide(ReplaceSchedule)

    create_mailing = provide(CreateRoleMailing)
    get_mailing_info = provide(GetMailingInfo)
    delete_mailing = provide(CancelMailing)

    get_nomination_by_id = provide(GetNominationById)
    get_nominations_page = provide(GetNominationsPage)

    get_settings = provide(GetSettings)
    update_settings = provide(UpdateSettings)

    create_subscription = provide(CreateSubscription)
    delete_subscription = provide(DeleteSubscription)
    get_subscriptions_page = provide(GetSubscriptionsPage)

    generate_ticket = provide(GenerateTicket)
    delete_ticket = provide(DeleteTicket)
    link_ticket = provide(LinkTicket)

    authenticate = provide(TgAuthenticate)
    get_user_by_id = provide(GetUserById)
    get_user_by_username = provide(GetUserByUsername)
    update_user = provide(UpdateUser)
    update_user_settings = provide(UpdateUserSettings)
    send_message = provide(SendMessageToUser)

    get_user_quest_details = provide(GetUserQuestStatus)
    get_quest_rating = provide(GetQuestRating)
    add_points = provide(AddPointsToUser)
    receive_achievement = provide(ReceiveAchievement)
    reset_quest = provide(ResetQuest)

    get_participants_page = provide(GetParticipantsPage)
    add_vote = provide(AddVote)
    cancel_vote = provide(CancelVote)
    get_voting_state = provide(GetVotingState)

    get_code_by_id = provide(GetCodeById)
    get_user_code = provide(GetUserCodeId)

    list_markets = provide(GetMarketsPage)
    get_market = provide(GetMarketById)
    update_market = provide(UpdateMarket)

    add_product = provide(CreateProduct)
    list_products = provide(GetProductsPage)
    get_product = provide(GetProductById)
    update_product = provide(UpdateProduct)
    create_market_by_participant = provide(CreateMarketByParticipant)
