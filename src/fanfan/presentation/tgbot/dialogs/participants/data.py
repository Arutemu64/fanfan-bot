from dataclasses import dataclass

from fanfan.core.vo.participant import ParticipantId


@dataclass(slots=True)
class ParticipantsViewerData:
    participant_id: ParticipantId | None = None

    # Query
    search_query: str | None = None
