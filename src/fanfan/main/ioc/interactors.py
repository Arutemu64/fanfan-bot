from dishka import Provider, Scope, provide

from fanfan.application.activities.read_activities_page import ReadActivitiesPage
from fanfan.application.activities.read_activity_by_id import ReadActivityById
from fanfan.application.codes.get_user_code_id import GetUserCodeId
from fanfan.application.codes.read_code_by_id import ReadCodeById
from fanfan.application.feedback.proceed_feedback import ProceedFeedback
from fanfan.application.feedback.send_feedback import SendFeedback
from fanfan.application.mailing.cancel_mailing import CancelMailing
from fanfan.application.mailing.create_role_mailing import CreateRoleMailing
from fanfan.application.mailing.read_mailing_info import ReadMailingInfo
from fanfan.application.mailing.send_personal_message import SendPersonalMessage
from fanfan.application.marketplace.create_market_by_participant import (
    CreateMarketByParticipant,
)
from fanfan.application.marketplace.create_product import CreateProduct
from fanfan.application.marketplace.read_market import ReadMarket
from fanfan.application.marketplace.read_markets_page import ReadMarketsPage
from fanfan.application.marketplace.read_product import ReadProduct
from fanfan.application.marketplace.read_products_page import ReadProductsPage
from fanfan.application.marketplace.update_market import UpdateMarket
from fanfan.application.marketplace.update_product import UpdateProduct
from fanfan.application.quest.add_points_to_user import AddPointsToUser
from fanfan.application.quest.get_rating_page_number_by_user import (
    GetRatingPageNumberByUser,
)
from fanfan.application.quest.read_achievements_page_for_user import (
    GetAchievementsPageForUser,
)
from fanfan.application.quest.read_quest_rating import GetQuestRating
from fanfan.application.quest.read_user_quest_details import GetUserQuestStats
from fanfan.application.quest.receive_achievement import ReceiveAchievement
from fanfan.application.quest.reset_quest import ResetQuest
from fanfan.application.schedule.get_page_number_by_event import (
    GetPageNumberByScheduleEvent,
)
from fanfan.application.schedule.management.move_event import MoveScheduleEvent
from fanfan.application.schedule.management.replace_schedule import ReplaceSchedule
from fanfan.application.schedule.management.revert_change import RevertScheduleChange
from fanfan.application.schedule.management.set_current_event import (
    SetCurrentScheduleEvent,
)
from fanfan.application.schedule.management.set_next_event import SetNextScheduleEvent
from fanfan.application.schedule.management.skip_event import SkipScheduleEvent
from fanfan.application.schedule.read_current_event import ReadCurrentScheduleEvent
from fanfan.application.schedule.read_event_by_public_id import (
    ReadScheduleEventByPublicId,
)
from fanfan.application.schedule.read_event_for_user import ReadScheduleEventForUser
from fanfan.application.schedule.read_schedule_page_for_user import (
    ReadSchedulePageForUser,
)
from fanfan.application.schedule.subscriptions.create_subscription import (
    CreateSubscription,
)
from fanfan.application.schedule.subscriptions.delete_subscription_by_event import (
    DeleteSubscriptionByEvent,
)
from fanfan.application.schedule.subscriptions.read_subscriptions_page import (
    GetSubscriptionsPage,
)
from fanfan.application.settings.get_settings import GetSettings
from fanfan.application.settings.update_settings import UpdateSettings
from fanfan.application.tickets.delete_ticket import DeleteTicket
from fanfan.application.tickets.generate_ticket import GenerateTicket
from fanfan.application.tickets.link_ticket import LinkTicket
from fanfan.application.users.authenticate import Authenticate
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.application.users.read_user_by_username import ReadUserByUsername
from fanfan.application.users.update_user import UpdateUser
from fanfan.application.users.update_user_settings import UpdateUserSettings
from fanfan.application.utils.import_from_c2 import ImportFromC2
from fanfan.application.utils.import_orders import ImportOrders
from fanfan.application.utils.proceed_order import ProceedOrder
from fanfan.application.utils.read_random_quote import ReadRandomQuote
from fanfan.application.voting.add_vote import AddVote
from fanfan.application.voting.cancel_vote import CancelVote
from fanfan.application.voting.read_nomination_for_user import ReadNominationForUser
from fanfan.application.voting.read_nominations_page_for_user import (
    ReadNominationsPageForUser,
)
from fanfan.application.voting.read_participants_page_for_user import (
    ReadParticipantsPageForUser,
)


class InteractorsProvider(Provider):
    scope = Scope.REQUEST

    get_achievements_page = provide(GetAchievementsPageForUser)

    get_activities_page = provide(ReadActivitiesPage)
    get_activity_by_id = provide(ReadActivityById)

    get_random_quote = provide(ReadRandomQuote)

    get_current_event = provide(ReadCurrentScheduleEvent)
    get_event_by_id = provide(ReadScheduleEventForUser)
    get_event_by_public_id = provide(ReadScheduleEventByPublicId)
    get_page_number_by_event = provide(GetPageNumberByScheduleEvent)
    get_schedule_page = provide(ReadSchedulePageForUser)

    move_event = provide(MoveScheduleEvent)
    set_current_event = provide(SetCurrentScheduleEvent)
    set_next_event = provide(SetNextScheduleEvent)
    skip_event = provide(SkipScheduleEvent)
    revert_change = provide(RevertScheduleChange)
    replace_schedule = provide(ReplaceSchedule)

    send_feedback = provide(SendFeedback)
    process_feedback = provide(ProceedFeedback)

    create_mailing = provide(CreateRoleMailing)
    get_mailing_info = provide(ReadMailingInfo)
    delete_mailing = provide(CancelMailing)

    get_nomination_by_id = provide(ReadNominationForUser)
    get_nominations_page = provide(ReadNominationsPageForUser)

    get_settings = provide(GetSettings)
    update_settings = provide(UpdateSettings)

    create_subscription = provide(CreateSubscription)
    delete_subscription = provide(DeleteSubscriptionByEvent)
    get_subscriptions_page = provide(GetSubscriptionsPage)

    generate_ticket = provide(GenerateTicket)
    delete_ticket = provide(DeleteTicket)
    link_ticket = provide(LinkTicket)

    authenticate = provide(Authenticate)
    get_user_by_id = provide(GetUserById)
    get_user_by_username = provide(ReadUserByUsername)
    update_user = provide(UpdateUser)
    update_user_settings = provide(UpdateUserSettings)
    send_message = provide(SendPersonalMessage)

    get_user_quest_details = provide(GetUserQuestStats)
    get_quest_rating = provide(GetQuestRating)
    get_rating_page_by_user = provide(GetRatingPageNumberByUser)
    add_points = provide(AddPointsToUser)
    receive_achievement = provide(ReceiveAchievement)
    reset_quest = provide(ResetQuest)

    get_participants_page = provide(ReadParticipantsPageForUser)
    add_vote = provide(AddVote)
    cancel_vote = provide(CancelVote)

    import_from_c2 = provide(ImportFromC2)
    import_tickets = provide(ImportOrders)
    proceed_timepad_order = provide(ProceedOrder)

    get_code_by_id = provide(ReadCodeById)
    get_user_code = provide(GetUserCodeId)

    list_markets = provide(ReadMarketsPage)
    get_market = provide(ReadMarket)
    update_market = provide(UpdateMarket)

    add_product = provide(CreateProduct)
    list_products = provide(ReadProductsPage)
    get_product = provide(ReadProduct)
    update_product = provide(UpdateProduct)
    create_market_by_participant = provide(CreateMarketByParticipant)
