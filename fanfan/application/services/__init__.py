from typing import Optional

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.services.event import EventService
from fanfan.application.services.nomination import NominationService
from fanfan.application.services.notification import NotificationService
from fanfan.application.services.quest import QuestService
from fanfan.application.services.schedule import ScheduleService
from fanfan.application.services.schedule_mgmt import ScheduleManagementService
from fanfan.application.services.settings import SettingsService
from fanfan.application.services.subscriptions import SubscriptionsService
from fanfan.application.services.ticket import TicketService
from fanfan.application.services.user import UserService
from fanfan.application.services.voting import VotingService
from fanfan.infrastructure.db import UnitOfWork


class ServicesHolder:
    def __init__(self, uow: UnitOfWork, identity: Optional[FullUserDTO]):
        self.uow = uow
        self.identity = identity

        self.events = EventService(uow, identity)
        self.nominations = NominationService(uow, identity)
        self.notifications = NotificationService(uow, identity)
        self.quest = QuestService(uow, identity)
        self.schedule = ScheduleService(uow, identity)
        self.schedule_mgmt = ScheduleManagementService(uow, identity)
        self.settings = SettingsService(uow, identity)
        self.subscriptions = SubscriptionsService(uow, identity)
        self.tickets = TicketService(uow, identity)
        self.users = UserService(uow, identity)
        self.voting = VotingService(uow, identity)
