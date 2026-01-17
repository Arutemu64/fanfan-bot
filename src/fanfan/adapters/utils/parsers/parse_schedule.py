import logging
import typing

import numpy as np
import pandas as pd

from fanfan.adapters.db.repositories.schedule_events import ScheduleEventsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.models.schedule_event import ScheduleEvent
from fanfan.core.vo.schedule_event import ScheduleEventPublicId

logger = logging.getLogger(__name__)

ORDER_INIT = 100.0
ORDER_STEP = 100.0


async def parse_schedule(
    file: typing.BinaryIO,
    events_repo: ScheduleEventsRepository,
    uow: UnitOfWork,
) -> None:
    schedule_df = pd.read_excel(
        file,
        converters={
            "public_id": int,
            "title": str,
            "duration": int,
            "nomination_title": str,
            "block_title": str,
        },
    )
    schedule_df = schedule_df.replace({np.nan: None})
    orphaned_events = await events_repo.get_all_events()
    order = ORDER_INIT
    async with uow:
        for _index, row in schedule_df.iterrows():
            existing_event = next(
                (e for e in orphaned_events if e.public_id == row["public_id"]), None
            )
            if existing_event:
                # Update event
                existing_event.title = row["title"]
                existing_event.duration = row["duration"]
                existing_event.block_title = row["block_title"]
                existing_event.nomination_title = row["nomination_title"]
                existing_event.order = order
                await events_repo.save_event(existing_event)
                orphaned_events.remove(existing_event)
                logger.info(
                    "Existing event was updated",
                    extra={"existing_event": existing_event},
                )
            else:
                # Create new event
                new_event = ScheduleEvent(
                    public_id=ScheduleEventPublicId(row["public_id"]),
                    title=row["title"],
                    duration=row["duration"],
                    block_title=row["block_title"],
                    nomination_title=row["nomination_title"],
                    order=order,
                    is_current=None,
                    is_skipped=False,
                )
                await events_repo.add_event(new_event)
                logger.info("New event was added", extra={"new_event": new_event})
            order += ORDER_STEP
        for e in orphaned_events:
            await events_repo.delete_event(e)
            logger.info("Orphaned event was deleted", extra={"deleted_event": e})
        await uow.commit()
