import logging
from dataclasses import dataclass

from fanfan.adapters.db.repositories.schedule_changes import ScheduleChangesRepository
from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.nats.events_broker import EventsBroker
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.events.notifications import CancelMailingEvent
from fanfan.core.exceptions.schedule import (
    OutdatedScheduleChange,
    ScheduleChangeNotFound,
)
from fanfan.core.models.schedule_change import ScheduleChangeType
from fanfan.core.services.schedule import ScheduleService
from fanfan.core.vo.schedule_change import ScheduleChangeId

logger = logging.getLogger(__name__)


@dataclass(slots=True, frozen=True)
class RevertScheduleChangeDTO:
    schedule_change_id: ScheduleChangeId


class RevertScheduleChange:
    def __init__(
        self,
        uow: UnitOfWork,
        schedule_changes_repo: ScheduleChangesRepository,
        schedule_repo: ScheduleEventsRepository,
        events_broker: EventsBroker,
        id_provider: IdProvider,
        service: ScheduleService,
    ):
        self.uow = uow
        self.schedule_changes_repo = schedule_changes_repo
        self.schedule_repo = schedule_repo
        self.events_broker = events_broker
        self.id_provider = id_provider
        self.service = service

    async def __call__(self, data: RevertScheduleChangeDTO) -> None:  # noqa: C901
        user = await self.id_provider.get_current_user()
        await self.service.ensure_user_can_manage_schedule(user)
        schedule_change = await self.schedule_changes_repo.get_schedule_change(
            data.schedule_change_id
        )
        if schedule_change is None:
            raise ScheduleChangeNotFound

        changed_event = await self.schedule_repo.get_event_by_id(
            schedule_change.changed_event_id
        )
        argument_event = await self.schedule_repo.get_event_by_id(
            schedule_change.argument_event_id
        )

        async with self.uow:
            if schedule_change.type is ScheduleChangeType.SET_AS_CURRENT:
                previous_event = argument_event
                current_event = await self.schedule_repo.get_current_event()

                if changed_event != current_event:
                    raise OutdatedScheduleChange

                if changed_event:
                    changed_event.is_current = None
                    await self.schedule_repo.save_event(changed_event)

                if previous_event:
                    previous_event.is_current = True
                    await self.schedule_repo.save_event(previous_event)

            if schedule_change.type is ScheduleChangeType.MOVED:
                place_after_event = argument_event

                if place_after_event:
                    place_before_event = await self.schedule_repo.get_next_by_order(
                        place_after_event.order
                    )
                    if place_before_event:
                        new_order = (
                            place_after_event.order + place_before_event.order
                        ) / 2
                    else:
                        new_order = place_after_event.order + 1
                else:
                    first_event = await self.schedule_repo.read_event_by_queue(1)
                    new_order = first_event.order - 1 if first_event else 1

                changed_event.order = new_order
                await self.schedule_repo.save_event(changed_event)

            if schedule_change.type is ScheduleChangeType.SKIPPED:
                changed_event.is_skipped = False
                await self.schedule_repo.save_event(changed_event)

            if schedule_change.type is ScheduleChangeType.UNSKIPPED:
                changed_event.is_skipped = True
                await self.schedule_repo.save_event(changed_event)

            await self.schedule_changes_repo.delete_schedule_change(schedule_change)
            await self.uow.commit()

            await self.events_broker.publish(
                CancelMailingEvent(mailing_id=schedule_change.mailing_id)
            )

            logger.info(
                "User %s reverted schedule change %s",
                user.id,
                data.schedule_change_id,
                extra={"schedule_change": schedule_change},
            )
