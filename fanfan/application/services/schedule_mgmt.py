from typing import Tuple

from fanfan.application.dto.event import EventDTO
from fanfan.application.exceptions.event import (
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
    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def skip_event(self, event_id: int) -> EventDTO:
        """Mark event as skipped
        @param event_id:
        @return: Skipped event
        """
        event = await self.uow.events.get_event(event_id)
        if not event:
            raise EventNotFound(event_id)

        current_event = await self.uow.events.get_current_event()
        if event is current_event:
            raise CurrentEventNotAllowed
        next_event = await self.uow.events.get_next_event()

        async with self.uow:
            event.skip = not event.skip
            await self.uow.session.flush([event])
            await self.uow.session.refresh(event, ["real_position"])
            await NotificationService(self.uow, self.identity).proceed_subscriptions(
                current_event_before=current_event,
                next_event_before=next_event,
                changed_events=[event],
            )
            await self.uow.commit()
            return event.to_dto()

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def swap_events(
        self,
        event1_id: int,
        event2_id: int,
    ) -> Tuple[EventDTO, EventDTO]:
        """Swap two schedule positions
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

        current_event = await self.uow.events.get_current_event()
        next_event = await self.uow.events.get_next_event()

        async with self.uow:
            event1.position, event2.position = event2.position, event1.position
            await self.uow.session.flush([event1, event2])
            await self.uow.session.refresh(event1, ["real_position"])
            await self.uow.session.refresh(event2, ["real_position"])
            await NotificationService(self.uow, self.identity).proceed_subscriptions(
                current_event_before=current_event,
                next_event_before=next_event,
                changed_events=[event1, event2],
            )
            await self.uow.commit()
            return event1.to_dto(), event2.to_dto()

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def set_current_event(self, event_id: int) -> EventDTO:
        """Set event as current
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
        next_event = await self.uow.events.get_next_event()

        async with self.uow:
            event.current = True
            await self.uow.session.flush([event])
            await NotificationService(self.uow, self.identity).proceed_subscriptions(
                current_event_before=current_event,
                next_event_before=next_event,
                changed_events=[event],
            )
            await self.uow.commit()
            return event.to_dto()

    @check_permission(allowed_roles=[UserRole.HELPER, UserRole.ORG])
    async def set_next_event(self) -> EventDTO:
        """Sets next event as current
        @return: Current event
        """
        current_event = await self.uow.events.get_current_event()
        if current_event:
            next_event = await self.uow.events.get_next_event()
            if not next_event:
                raise NoNextEvent
        else:
            next_event = await self.uow.events.get_event_by_real_position(1)
            if not next_event:
                raise EventNotFound
        return await self.set_current_event(next_event.id)
