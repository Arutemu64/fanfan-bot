import logging
from dataclasses import dataclass, replace

from fanfan.adapters.db.repositories.schedule_blocks import ScheduleBlocksRepository
from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.models.schedule_block import ScheduleBlock
from fanfan.core.models.schedule_event import ScheduleEvent
from fanfan.core.vo.participant import ParticipantId
from fanfan.core.vo.schedule_event import ScheduleEventPublicId

ORDER_INIT = 100.0
ORDER_STEP = 100.0

logger = logging.getLogger(__name__)


@dataclass(frozen=True, slots=True, kw_only=True)
class ScheduleBlockEntry:
    title: str


@dataclass(frozen=True, slots=True, kw_only=True)
class ScheduleEventEntry:
    public_id: ScheduleEventPublicId
    title: str
    duration: int
    participant_id: ParticipantId | None


@dataclass(frozen=True, slots=True, kw_only=True)
class NewSchedule:
    entries: list[ScheduleBlockEntry | ScheduleEventEntry]


class ReplaceSchedule:
    def __init__(
        self,
        events_repo: ScheduleEventsRepository,
        blocks_repo: ScheduleBlocksRepository,
        uow: UnitOfWork,
    ) -> None:
        self.events_repo = events_repo
        self.blocks_repo = blocks_repo
        self.uow = uow

    async def __call__(self, new_schedule: NewSchedule):
        if not new_schedule.entries:
            msg = "Schedule must contain at least one entry."
            raise ValueError(msg)
        async with self.uow:
            await self.blocks_repo.delete_all_blocks()
            orphaned_events = await self.events_repo.get_all_events()
            order = ORDER_INIT
            for entry in new_schedule.entries:
                if isinstance(entry, ScheduleBlockEntry):
                    new_block = ScheduleBlock(
                        title=entry.title,
                        start_order=order,
                    )
                    logger.info("New block was added", extra={"new_block": new_block})
                    await self.blocks_repo.add_block(new_block)
                elif isinstance(entry, ScheduleEventEntry):
                    # Try to locate existing event to preserve user subscriptions
                    existing_event = None
                    if entry.participant_id:
                        existing_event = (
                            await self.events_repo.get_event_by_participant_id(
                                entry.participant_id
                            )
                        )
                    if existing_event:
                        orphaned_events.remove(existing_event)
                        existing_event = replace(
                            existing_event,
                            public_id=entry.public_id,
                            title=entry.title,
                            duration=entry.duration,
                            order=order,
                            participant_id=entry.participant_id,
                        )
                        await self.events_repo.save_event(existing_event)
                        logger.info(
                            "Existing event was updated",
                            extra={"existing_event": existing_event},
                        )
                    else:
                        for e in orphaned_events:
                            if e.public_id == entry.public_id:
                                await self.events_repo.delete_event(e)
                                logger.info(
                                    "Event %s was deleted to free public ID %s",
                                    e.id,
                                    e.public_id,
                                    extra={"deleted_event": e},
                                )
                        new_event = ScheduleEvent(
                            public_id=entry.public_id,
                            title=entry.title,
                            duration=entry.duration,
                            order=order,
                            is_current=None,
                            is_skipped=False,
                            participant_id=entry.participant_id,
                        )
                        await self.events_repo.add_event(new_event)
                        logger.info(
                            "New event was added", extra={"new_event": new_event}
                        )
                order += ORDER_STEP
            for e in orphaned_events:
                await self.events_repo.delete_event(e)
                logger.info("Orphaned event was deleted", extra={"deleted_event": e})
            await self.uow.commit()
