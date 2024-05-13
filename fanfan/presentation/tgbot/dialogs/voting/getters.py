from aiogram_dialog import DialogManager

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions.voting import VoteNotFound
from fanfan.application.holder import AppHolder

from .constants import (
    DATA_SEARCH_QUERY,
    DATA_SELECTED_NOMINATION_ID,
    DATA_USER_VOTE_ID,
    ID_NOMINATIONS_SCROLL,
    ID_VOTING_SCROLL,
)


async def nominations_getter(
    dialog_manager: DialogManager,
    user: FullUserDTO,
    app: AppHolder,
    **kwargs,
):
    page = await app.voting.get_nominations_page(
        page_number=await dialog_manager.find(ID_NOMINATIONS_SCROLL).get_page(),
        nominations_per_page=user.settings.items_per_page,
        user_id=user.id,
    )
    nominations_list = []
    for nomination in page.items:
        nominations_list.append(
            (
                nomination.id,
                f"{nomination.title} ✅" if nomination.user_vote else nomination.title,
            ),
        )
    return {
        "nominations_list": nominations_list,
        "pages": page.total_pages,
    }


async def participants_getter(
    dialog_manager: DialogManager,
    user: FullUserDTO,
    app: AppHolder,
    **kwargs,
):
    nomination = await app.voting.get_nomination(
        dialog_manager.dialog_data[DATA_SELECTED_NOMINATION_ID],
    )
    page = await app.voting.get_participants_page(
        nomination_id=dialog_manager.dialog_data[DATA_SELECTED_NOMINATION_ID],
        page_number=await dialog_manager.find(ID_VOTING_SCROLL).get_page(),
        participants_per_page=user.settings.items_per_page,
        user_id=user.id,
        search_query=dialog_manager.dialog_data.get(DATA_SEARCH_QUERY, None),
    )
    try:
        user_vote = await app.voting.get_vote_by_nomination(
            user_id=user.id,
            nomination_id=dialog_manager.dialog_data[DATA_SELECTED_NOMINATION_ID],
        )
        dialog_manager.dialog_data[DATA_USER_VOTE_ID] = user_vote.id
    except VoteNotFound:
        dialog_manager.dialog_data[DATA_USER_VOTE_ID] = None
    return {
        "nomination_title": nomination.title,
        "pages": page.total_pages,
        "participants": page.items,
        "voted": True if dialog_manager.dialog_data[DATA_USER_VOTE_ID] else False,
    }
