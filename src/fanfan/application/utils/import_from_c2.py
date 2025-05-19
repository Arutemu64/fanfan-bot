import logging
import time
from dataclasses import dataclass
from datetime import timedelta

from fanfan.adapters.api.cosplay2.client import Cosplay2Client
from fanfan.adapters.api.cosplay2.dto.requests import RequestStatus
from fanfan.adapters.api.cosplay2.exceptions import (
    NoCosplay2ConfigProvided,
)
from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.adapters.utils.rate_lock import RateLockFactory
from fanfan.core.models.nomination import Nomination
from fanfan.core.models.participant import Participant
from fanfan.core.vo.nomination import NominationId
from fanfan.core.vo.participant import ParticipantId

logger = logging.getLogger(__name__)

# Limits
IMPORT_FROM_C2_LIMIT_NAME = "import_from_c2"
IMPORT_FROM_C2_TIMEOUT = timedelta(minutes=1).seconds


@dataclass(slots=True, frozen=True)
class ImportFromC2Result:
    new_topics: int
    new_requests: int
    elapsed_time: int


class ImportFromC2:
    def __init__(
        self,
        cosplay2: Cosplay2Client | None,
        participants_repo: ParticipantsRepository,
        nominations_repo: NominationsRepository,
        uow: UnitOfWork,
        rate_limit_factory: RateLockFactory,
    ):
        self.cosplay2 = cosplay2
        self.participants_repo = participants_repo
        self.nominations_repo = nominations_repo
        self.uow = uow
        self.rate_limit_factory = rate_limit_factory

    async def __call__(self) -> ImportFromC2Result:
        if self.cosplay2 is None:
            raise NoCosplay2ConfigProvided
        lock = self.rate_limit_factory(
            limit_name=IMPORT_FROM_C2_LIMIT_NAME,
            cooldown_period=IMPORT_FROM_C2_TIMEOUT,
            blocking=False,
            lock_timeout=timedelta(minutes=5).seconds,
        )
        new_topics, new_requests = 0, 0
        start = time.time()
        async with lock, self.uow:
            topics = await self.cosplay2.get_topics_list()
            for topic in topics:
                nomination = await self.nominations_repo.get_nomination_by_id(
                    NominationId(topic.id)
                )
                if nomination:
                    # Update nomination
                    nomination.code = topic.card_code
                    nomination.title = topic.title
                    nomination = await self.nominations_repo.save_nomination(nomination)
                    logger.info(
                        "Nomination %s updated",
                        nomination.id,
                        extra={"nomination": nomination},
                    )
                else:
                    # Create new one
                    nomination = Nomination(
                        id=NominationId(topic.id),
                        code=topic.card_code,
                        title=topic.title,
                        is_votable=False,
                    )
                    nomination = await self.nominations_repo.add_nomination(nomination)
                    new_topics += 1
                    logger.info(
                        "Nomination %s added",
                        nomination.id,
                        extra={"nomination": nomination},
                    )
            # Import requests into participants
            requests = await self.cosplay2.get_all_requests()
            for request in requests:
                if request.status is not RequestStatus.APPROVED:
                    continue
                if not request.voting_title:
                    logger.warning("Request %s lacks voting_title", request.id)
                    continue
                participant = await self.participants_repo.get_participant_by_id(
                    participant_id=ParticipantId(request.id)
                )
                if participant:
                    participant.title = request.voting_title
                    participant.nomination_id = NominationId(request.topic_id)
                    participant.voting_number = request.voting_number
                    participant = await self.participants_repo.save_participant(
                        participant
                    )
                    logger.info(
                        "Participant %s updated",
                        participant.id,
                        extra={"participant": participant},
                    )
                else:
                    participant = Participant(
                        id=ParticipantId(request.id),
                        title=request.voting_title,
                        nomination_id=NominationId(request.topic_id),
                        voting_number=request.voting_number,
                    )
                    await self.participants_repo.add_participant(participant)
                    new_requests += 1
                    logger.info(
                        "Participant %s added",
                        participant.id,
                        extra={"participant": participant},
                    )
            await self.uow.commit()
        end = time.time()
        return ImportFromC2Result(
            new_topics=new_topics,
            new_requests=new_requests,
            elapsed_time=int(end - start),
        )
