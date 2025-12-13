from aiogram_dialog import Dialog

from .list_voting_nominations import voting_nominations_window
from .list_voting_participants import voting_participants_window

dialog = Dialog(voting_nominations_window, voting_participants_window)
