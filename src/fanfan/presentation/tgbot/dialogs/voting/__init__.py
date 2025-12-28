from aiogram import Router
from aiogram_dialog import Dialog

from .handlers import voting_handlers_router
from .list_voting_nominations import voting_nominations_window
from .list_voting_participants import voting_participants_window

voting_router = Router(name="voting_router")

voting_dialog = Dialog(voting_nominations_window, voting_participants_window)

voting_router.include_routers(voting_handlers_router, voting_dialog)
