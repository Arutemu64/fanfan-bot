from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class VoteDTO:
    id: int
    user_id: int
    participant_id: int
