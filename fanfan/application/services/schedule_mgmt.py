import time
from typing import Tuple

from fanfan.application.dto.event import EventDTO
from fanfan.application.exceptions.event import (
    AnnounceTooFast,
    CurrentEventNotAllowed,
    EventNotFound,
    NoNextEvent,
    SameEventsAreNotAllowed,
    SkippedEventNotAllowed,
)
from fanfan.application.services.access import check_permission
from fanfan.application.services.base import BaseService
from fanfan.application.services.notification import NotificationService
from fanfan.common.enums import UserRole


class ScheduleManagementService(BaseService):
    async def _throttle_global_announcement(self) -> None:
        settings = await self.uow.settings.get_settings()
        timestamp = time.time()
        if (
            timestamp - settings.announcement_timestamp
        ) < settings.announcement_timeout:
            raise AnnounceTooFast(
                settings.announcement_timeout,
                int(
                    settings.announcement_timestamp
                    + settings.announcement_timeout
                    - timestamp
                ),
            )
        else:
            settings.announcement_timestamp = timestamp

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def skip_event(self, event_id: int) -> EventDTO:
        """
        Mark event as skipped
        @param event_id:
        @return: Skipped event
        """
        event = await self.uow.events.get_event(event_id)
        if not event:
            raise EventNotFound(event_id)

        send_global_announcement = False
        current_event = await self.uow.events.get_current_event()
        if current_event:
            if event is current_event:
                raise CurrentEventNotAllowed
            next_event = await self.uow.events.get_next_event(current_event.id)
            if (event is next_event) or (event.position == current_event.position + 1):
                await self._throttle_global_announcement()
                send_global_announcement = True

        async with self.uow:
            event.skip = not event.skip
            await self.uow.commit()
            await self.uow.session.refresh(event)
            await NotificationService(self.uow, self.identity).proceed_subscriptions(
                send_global_announcement=send_global_announcement
            )
            return event.to_dto()

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def swap_events(
        self, event1_id: int, event2_id: int
    ) -> Tuple[EventDTO, EventDTO]:
        """
        Swap two schedule positions
        @param event1_id:
        @param event2_id:
        @return: Tuple of both schedule
        """
        if event1_id == event2_id:
            raise SameEventsAreNotAllowed
        event1 = await self.uow.events.get_event(event1_id)
        if not event1:
            raise EventNotFound(event1_id)
        event2 = await self.uow.events.get_event(event2_id)
        if not event2:
            raise EventNotFound(event2_id)

        send_global_announcement = False
        current_event = await self.uow.events.get_current_event()
        if current_event:
            next_event = await self.uow.events.get_next_event(current_event.id)
            if {event1, event2}.intersection({current_event, next_event}):
                await self._throttle_global_announcement()
                send_global_announcement = True

        async with self.uow:
            event1.position, event2.position = event2.position, event1.position
            await self.uow.commit()
            await self.uow.session.refresh(event1)
            await self.uow.session.refresh(event2)
            await NotificationService(self.uow, self.identity).proceed_subscriptions(
                send_global_announcement=send_global_announcement
            )
            return event1.to_dto(), event2.to_dto()

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def set_current_event(self, event_id: int) -> EventDTO:
        """
        Set event as current
        @param event_id:
        @return: Current event
        """
        event = await self.uow.events.get_event(event_id)
        if not event:
            raise EventNotFound
        if event.skip:
            raise SkippedEventNotAllowed

        current_event = await self.uow.events.get_current_event()
        if current_event:
            if event is current_event:
                raise CurrentEventNotAllowed
            current_event.current = None
            await self.uow.session.flush([current_event])

        async with self.uow:
            await self._throttle_global_announcement()
            event.current = True
            await self.uow.commit()
            await NotificationService(self.uow, self.identity).proceed_subscriptions(
                send_global_announcement=True
            )
            return event.to_dto()

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def set_next_event(self) -> EventDTO:
        """
        Sets next event as current
        @return: Current event
        """
        current_event = await self.uow.events.get_current_event()
        if current_event:
            next_event = await self.uow.events.get_next_event(current_event.id)
            if not next_event:
                raise NoNextEvent
        else:
            next_event = await self.uow.events.get_event_by_real_position(1)
            if not next_event:
                raise EventNotFound
        return await self.set_current_event(next_event.id)
