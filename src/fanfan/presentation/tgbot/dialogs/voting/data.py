from dataclasses import dataclass

from fanfan.core.vo.nomination import NominationId
from fanfan.core.vo.vote import VoteId

DATA_NOMINATION_ID = "nomination_id"


@dataclass(slots=True)
class VotingDialogData:
    nomination_id: NominationId | None = None
    user_vote_id: VoteId | None = None
