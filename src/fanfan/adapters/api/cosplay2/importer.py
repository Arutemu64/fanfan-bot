import logging
from dataclasses import replace

from fanfan.adapters.api.cosplay2.client import Cosplay2Client
from fanfan.adapters.api.cosplay2.config import Cosplay2Config
from fanfan.adapters.api.cosplay2.dto.requests import RequestStatus
from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.adapters.db.repositories.participants import ParticipantsRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.models.nomination import Nomination
from fanfan.core.models.participant import Participant, ParticipantValue
from fanfan.core.vo.nomination import NominationId
from fanfan.core.vo.participant import ParticipantId

logger = logging.getLogger(__name__)


class Cosplay2Importer:
    def __init__(
        self,
        config: Cosplay2Config,
        client: Cosplay2Client,
        participants_repo: ParticipantsRepository,
        nominations_repo: NominationsRepository,
        uow: UnitOfWork,
    ):
        self.config = config
        self.client = client
        self.participants_repo = participants_repo
        self.nominations_repo = nominations_repo
        self.uow = uow

    async def _sync_topics(self) -> int:
        new_topics = 0
        topics = await self.client.get_topics_list()
        for topic in topics:
            nomination = await self.nominations_repo.get_nomination_by_id(
                NominationId(topic.id)
            )
            if nomination:
                # Update nomination
                nomination = replace(
                    nomination, code=topic.card_code, title=topic.title
                )
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
        return new_topics

    async def _sync_requests(self):
        new_requests = 0
        requests = await self.client.get_all_requests()
        values = await self.client.get_all_values()
        for request in requests:
            # Checks
            if request.status is not RequestStatus.APPROVED:
                continue
            if not request.voting_title:
                logger.warning("Request %s lacks voting_title", request.id)
                continue

            # Query existing participant
            participant = await self.participants_repo.get_participant_by_id(
                participant_id=ParticipantId(request.id)
            )

            # Convert request values to participant values
            request_values = [v for v in values if v.request_id == request.id]
            participant_values = [
                ParticipantValue(title=r.title, type=r.type, value=r.value)
                for r in request_values
            ]

            # Update or create participant
            if participant:
                participant = replace(
                    participant,
                    title=request.voting_title,
                    nomination_id=NominationId(request.topic_id),
                    voting_number=request.voting_number,
                    values=participant_values,
                )
                participant = await self.participants_repo.save_participant(participant)
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
                    values=participant_values,
                )
                await self.participants_repo.add_participant(participant)
                new_requests += 1
                logger.info(
                    "Participant %s added",
                    participant.id,
                    extra={"participant": participant},
                )
        return new_requests

    async def sync_all(self):
        async with self.uow:
            await self._sync_topics()
            await self._sync_requests()
            await self.uow.commit()
