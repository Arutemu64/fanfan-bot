import logging
from dataclasses import dataclass
from datetime import timedelta

from sqlalchemy.exc import IntegrityError

from fanfan.adapters.cosplay2.client import Cosplay2Client
from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.application.common.limiter import Limiter
from fanfan.core.models.nomination import NominationCode, NominationId, NominationModel
from fanfan.core.models.participant import ParticipantId, ParticipantModel

logger = logging.getLogger(__name__)

# Limits
IMPORT_FROM_C2_LIMIT_NAME = "import_from_c2"
IMPORT_FROM_C2_TIMEOUT = timedelta(minutes=30).seconds


@dataclass(slots=True, frozen=True)
class ImportFromC2Result:
    topics_merged: int
    requests_merged: int
    requests_failed: int


class ImportFromC2:
    def __init__(
        self,
        cosplay2: Cosplay2Client,
        participants_repo: ParticipantsRepository,
        nominations_repo: NominationsRepository,
        uow: UnitOfWork,
        limiter: Limiter,
    ):
        self.cosplay2 = cosplay2
        self.participants_repo = participants_repo
        self.nominations_repo = nominations_repo
        self.uow = uow
        self.limiter = limiter

    async def __call__(self) -> ImportFromC2Result:
        async with self.limiter(
            limit_name=IMPORT_FROM_C2_LIMIT_NAME,
            limit_timeout=IMPORT_FROM_C2_TIMEOUT,
            blocking=False,
            lock_timeout=timedelta(minutes=5).seconds,
        ):
            topics_merged, requests_merged, requests_failed = 0, 0, 0
            # Import topics into nominations
            topics = await self.cosplay2.get_topics_list()
            for topic in topics:
                async with self.uow:
                    await self.nominations_repo.merge_nomination(
                        NominationModel(
                            id=NominationId(topic.id),
                            code=NominationCode(topic.card_code),
                            title=topic.title,
                        )
                    )
                    await self.uow.commit()
                    topics_merged += 1
            # Import requests into participants
            requests = await self.cosplay2.get_all_requests()
            for request in requests:
                if request.voting_title and request.status.APPROVED:
                    logger.info(
                        "Importing request %s", request.id, extra={"request": request}
                    )
                    async with self.uow:
                        try:
                            participant = (
                                await self.participants_repo.merge_participant(
                                    ParticipantModel(
                                        id=ParticipantId(request.id),
                                        title=request.voting_title,
                                        nomination_id=NominationId(request.topic_id),
                                    )
                                )
                            )
                            await self.uow.commit()
                            requests_merged += 1
                        except IntegrityError:
                            await self.uow.rollback()
                            logger.warning(
                                "Failed to merge request %s",
                                request.id,
                                extra={"request": request},
                            )
                            requests_failed += 1
                        else:
                            logger.info(
                                "Request %s merged",
                                participant.id,
                                extra={"participant": participant},
                            )
            return ImportFromC2Result(topics_merged, requests_merged, requests_failed)