import logging
import typing

import numpy as np
import pandas as pd
from adaptix import Retort

from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.application.schedule.management.replace_schedule import (
    NewSchedule,
    ReplaceSchedule,
    ScheduleBlockEntry,
    ScheduleEventEntry,
)
from fanfan.core.models.participant import ParticipantId, ParticipantVotingNumber
from fanfan.core.models.schedule_event import ScheduleEventPublicId

logger = logging.getLogger(__name__)


async def parse_schedule(
    file: typing.BinaryIO,
    replace_schedule: ReplaceSchedule,
    participants_repo: ParticipantsRepository,
    nominations_repo: NominationsRepository,
) -> None:
    """
    Parses schedule from Excel file.
    Use "converters" dict from down below as a reference
    (those keys must be header)
    Each line - single schedule entry (block or event)
    :param file:
    :param replace_schedule:
    :param participants_repo:
    :param nominations_repo:
    :return:
    """
    # Use adaptix to safely parse types
    retort = Retort()
    entries: list[ScheduleEventEntry | ScheduleBlockEntry] = []
    schedule_df = pd.read_excel(
        file,
        converters={
            # Event
            "event_public_id": ScheduleEventPublicId,
            "event_title": str,
            "event_duration": int,
            "event_participant_id": ParticipantId,
            "event_participant_voting_number": ParticipantVotingNumber,
            "event_participant_nomination_code": str,
            # Block
            "block_title": str,
        },
    )
    schedule_df = schedule_df.replace({np.nan: None})
    for _index, row in schedule_df.iterrows():
        if row.get("event_public_id"):
            # Event line
            participant_id = row.get("event_participant_id")
            if row.get("event_participant_voting_number"):
                nomination = await nominations_repo.get_nomination_by_code(
                    nomination_code=row["event_participant_nomination_code"]
                )
                if nomination:
                    participant = (
                        await participants_repo.get_participant_by_voting_number(
                            nomination_id=nomination.id,
                            voting_number=row["event_participant_voting_number"],
                        )
                    )
                    if participant:
                        participant_id = participant.id
            event = retort.load(
                {
                    "public_id": row["event_public_id"],
                    "title": row["event_title"],
                    "duration": row["event_duration"],
                    "participant_id": participant_id,
                },
                ScheduleEventEntry,
            )
            entries.append(event)
        elif row.get("block_title"):
            block = retort.load({"title": row["block_title"]}, ScheduleBlockEntry)
            entries.append(block)
    schedule = NewSchedule(entries=entries)
    await replace_schedule(schedule)
