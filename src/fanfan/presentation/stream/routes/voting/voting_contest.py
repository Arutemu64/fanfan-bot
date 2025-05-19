from dishka import FromDishka
from dishka.integrations.faststream import inject
from faststream.nats import NatsRouter, PullSub

from fanfan.adapters.db.repositories.flags import FlagsRepository
from fanfan.adapters.db.repositories.nominations import NominationsRepository
from fanfan.adapters.db.repositories.votes import VotesRepository
from fanfan.adapters.db.uow import UnitOfWork
from fanfan.core.events.voting import VoteUpdatedEvent
from fanfan.core.models.flag import Flag
from fanfan.presentation.stream.jstream import stream

VOTING_CONTEST_FLAG_NAME = "voting_contest"

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
    flags_repo: FromDishka[FlagsRepository],
    votes_repo: FromDishka[VotesRepository],
    nominations_repo: FromDishka[NominationsRepository],
    uow: FromDishka[UnitOfWork],
):
    # Get count of current user votes and total votable nominations
    user_votes_count = await votes_repo.count_user_votes(data.vote.user_id)
    votable_nominations_count = await nominations_repo.count_votable_nominations()

    # Check existing user flag
    flag = await flags_repo.get_flag_by_user(
        user_id=data.vote.user_id, flag_name=VOTING_CONTEST_FLAG_NAME
    )

    # If it exists, let's check if it's still valid
    if flag:
        if user_votes_count < votable_nominations_count:
            async with uow:
                await flags_repo.delete_flag(flag)
                await uow.commit()

    # If it's not - check if we can create it
    else:
        if user_votes_count >= votable_nominations_count:
            async with uow:
                flag = Flag(
                    flag_name=VOTING_CONTEST_FLAG_NAME, user_id=data.vote.user_id
                )
                await flags_repo.add_flag(flag)
                await uow.commit()
