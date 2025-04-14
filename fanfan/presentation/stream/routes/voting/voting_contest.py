from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream.nats import NatsRouter, PullSub

from fanfan.adapters.db.repositories.contest import ContestRepository
from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.adapters.db.repositories.votes import VotesRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.events.voting import VoteUpdatedEvent
from fanfan.core.models.contest import ContestEntry
from fanfan.presentation.stream.jstream import stream

VOTING_CONTEST_NAME = "voting"

router = NatsRouter()


@router.subscriber(
    "vote.updated",
    stream=stream,
    pull_sub=PullSub(),
    durable="vote_updated",
)
@inject
async def check_voting_contest_entry(
    data: VoteUpdatedEvent,
    contest_repo: FromDishka[ContestRepository],
    votes_repo: FromDishka[VotesRepository],
    nominations_repo: FromDishka[NominationsRepository],
    uow: FromDishka[UnitOfWork],
):
    # Get count of current user votes and total votable nominations
    user_votes_count = await votes_repo.count_user_votes(data.vote.user_id)
    votable_nominations_count = await nominations_repo.count_nominations(
        only_votable=True
    )

    # Check existing user contest entry
    contest_entry = await contest_repo.get_user_contest_entry(
        user_id=data.vote.user_id, contest_name=VOTING_CONTEST_NAME
    )

    # If it exists, let's check if it's still valid
    if contest_entry:
        if user_votes_count < votable_nominations_count:
            async with uow:
                await contest_repo.delete_contest_entry(contest_entry.id)
                await uow.commit()

    # If it's not - check if we can create it
    else:
        if user_votes_count >= votable_nominations_count:
            async with uow:
                contest_entry = ContestEntry(
                    contest_name=VOTING_CONTEST_NAME, user_id=data.vote.user_id
                )
                await contest_repo.add_contest_entry(contest_entry)
                await uow.commit()
