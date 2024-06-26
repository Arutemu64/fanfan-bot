from typing import Optional

from fanfan.application.dto.user import FullUserDTO
from fanfan.infrastructure.db import UnitOfWork


class AppHolder:
    def __init__(self, uow: UnitOfWork, identity: Optional[FullUserDTO]):
        self.uow = uow
        self.identity = identity

        from fanfan.application.services import (
            ActivitiesService,
            CommonService,
            FeedbackService,
            NotificationService,
            QRService,
            QuestService,
            ScheduleManagementService,
            ScheduleService,
            SettingsService,
            SubscriptionsService,
            TicketService,
            UserService,
            VotingService,
        )

        self.schedule = ScheduleService(uow, identity)
        self.notifications = NotificationService(uow, identity)
        self.quest = QuestService(uow, identity)
        self.schedule = ScheduleService(uow, identity)
        self.schedule_mgmt = ScheduleManagementService(uow, identity)
        self.settings = SettingsService(uow, identity)
        self.subscriptions = SubscriptionsService(uow, identity)
        self.tickets = TicketService(uow, identity)
        self.users = UserService(uow, identity)
        self.voting = VotingService(uow, identity)
        self.common = CommonService(uow, identity)
        self.qr = QRService(uow, identity)
        self.feedback = FeedbackService(uow, identity)
        self.activities = ActivitiesService(uow, identity)
