from dishka import Provider, Scope, provide

from fanfan.application.activities.get_activity_by_id import GetActivityById
from fanfan.application.activities.list_activities import ListActivities
from fanfan.application.codes.get_code_by_id import GetCodeById
from fanfan.application.codes.get_user_code_id import GetUserCodeId
from fanfan.application.cosplay2.sync_cosplay2 import SyncCosplay2
from fanfan.application.etc.get_random_quote import GetRandomQuote
from fanfan.application.marketplace.create_market_by_participant import (
    CreateMarketByParticipant,
)
from fanfan.application.marketplace.create_product import CreateProduct
from fanfan.application.marketplace.get_market_by_id import GetMarketById
from fanfan.application.marketplace.get_product_by_id import GetProductById
from fanfan.application.marketplace.list_markets import ListMarkets
from fanfan.application.marketplace.list_products import ListProducts
from fanfan.application.marketplace.update_market import UpdateMarket
from fanfan.application.marketplace.update_product import UpdateProduct
from fanfan.application.nominations.list_nominations import ListNominations
from fanfan.application.notifications.cancel_mailing import CancelMailing
from fanfan.application.notifications.create_role_mailing import CreateRoleMailing
from fanfan.application.notifications.get_mailing_info import GetMailingInfo
from fanfan.application.notifications.send_message_to_user import SendMessageToUser
from fanfan.application.participants.get_participant_by_id import GetParticipantById
from fanfan.application.participants.list_participants import ListParticipants
from fanfan.application.quest.add_points_to_user import AddPointsToUser
from fanfan.application.quest.get_achievements_page import (
    GetAchievementsPage,
)
from fanfan.application.quest.get_quest_rating import GetQuestRating
from fanfan.application.quest.get_user_quest_status import GetUserQuestStatus
from fanfan.application.quest.receive_achievement import ReceiveAchievement
from fanfan.application.quest.reset_quest import ResetQuest
from fanfan.application.schedule.get_schedule_event_by_id import GetScheduleEventById
from fanfan.application.schedule.list_schedule import (
    ListSchedule,
)
from fanfan.application.schedule.management.move_event import MoveScheduleEvent
from fanfan.application.schedule.management.revert_change import RevertScheduleChange
from fanfan.application.schedule.management.set_current_event import (
    SetCurrentScheduleEvent,
)
from fanfan.application.schedule.management.set_next_event import SetNextScheduleEvent
from fanfan.application.schedule.management.toggle_event_skip import (
    ToggleScheduleEventSkip,
)
from fanfan.application.schedule.subscriptions.create_subscription import (
    CreateSubscription,
)
from fanfan.application.schedule.subscriptions.delete_subscription import (
    DeleteSubscription,
)
from fanfan.application.settings.get_settings import GetSettings
from fanfan.application.settings.update_settings import UpdateSettings
from fanfan.application.tickets.delete_ticket import DeleteTicket
from fanfan.application.tickets.generate_ticket import GenerateTicket
from fanfan.application.tickets.use_ticket import UseTicket
from fanfan.application.ticketscloud.proceed_tcloud_webhook import ProceedTCloudWebhook
from fanfan.application.ticketscloud.sync_tcloud import SyncTCloud
from fanfan.application.users.get_current_user import GetCurrentUser
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.application.users.get_user_by_username import GetUserByUsername
from fanfan.application.users.tg_authenticate import TgAuthenticate
from fanfan.application.users.update_user import UpdateUser
from fanfan.application.users.update_user_settings import UpdateUserSettings
from fanfan.application.voting.add_vote import AddVote
from fanfan.application.voting.cancel_vote import CancelVote
from fanfan.application.voting.get_voting_nomination_by_id import (
    GetVotingNominationById,
)
from fanfan.application.voting.get_voting_state import GetVotingState
from fanfan.application.voting.list_voting_nominations import (
    ListVotingNominations,
)
from fanfan.application.voting.list_voting_participants import (
    ListVotingParticipants,
)


class InteractorsProvider(Provider):
    scope = Scope.REQUEST

    get_achievements_page = provide(GetAchievementsPage)

    get_activities_page = provide(ListActivities)
    get_activity_by_id = provide(GetActivityById)

    get_random_quote = provide(GetRandomQuote)

    get_event_by_id = provide(GetScheduleEventById)
    get_schedule_page = provide(ListSchedule)

    move_event = provide(MoveScheduleEvent)
    set_current_event = provide(SetCurrentScheduleEvent)
    set_next_event = provide(SetNextScheduleEvent)
    toggle_event_skip = provide(ToggleScheduleEventSkip)
    revert_change = provide(RevertScheduleChange)

    create_mailing = provide(CreateRoleMailing)
    get_mailing_info = provide(GetMailingInfo)
    delete_mailing = provide(CancelMailing)

    get_nomination_by_id = provide(GetVotingNominationById)
    get_nominations_page = provide(ListVotingNominations)

    get_settings = provide(GetSettings)
    update_settings = provide(UpdateSettings)

    create_subscription = provide(CreateSubscription)
    delete_subscription = provide(DeleteSubscription)

    generate_ticket = provide(GenerateTicket)
    delete_ticket = provide(DeleteTicket)
    use_ticket = provide(UseTicket)

    authenticate = provide(TgAuthenticate)
    get_user_by_id = provide(GetUserById)
    get_user_by_username = provide(GetUserByUsername)
    get_current_user = provide(GetCurrentUser)
    update_user = provide(UpdateUser)
    update_user_settings = provide(UpdateUserSettings)
    send_message = provide(SendMessageToUser)

    get_user_quest_details = provide(GetUserQuestStatus)
    get_quest_rating = provide(GetQuestRating)
    add_points = provide(AddPointsToUser)
    receive_achievement = provide(ReceiveAchievement)
    reset_quest = provide(ResetQuest)

    get_participants_page = provide(ListVotingParticipants)
    add_vote = provide(AddVote)
    cancel_vote = provide(CancelVote)
    get_voting_state = provide(GetVotingState)

    get_code_by_id = provide(GetCodeById)
    get_user_code = provide(GetUserCodeId)

    list_markets = provide(ListMarkets)
    get_market = provide(GetMarketById)
    update_market = provide(UpdateMarket)

    add_product = provide(CreateProduct)
    list_products = provide(ListProducts)
    get_product = provide(GetProductById)
    update_product = provide(UpdateProduct)
    create_market_by_participant = provide(CreateMarketByParticipant)

    list_participants = provide(ListParticipants)
    get_participant_by_id = provide(GetParticipantById)

    list_nominations = provide(ListNominations)

    sync_tcloud = provide(SyncTCloud)
    proceed_tcloud_webhook = provide(ProceedTCloudWebhook)

    sync_cosplay2 = provide(SyncCosplay2)
