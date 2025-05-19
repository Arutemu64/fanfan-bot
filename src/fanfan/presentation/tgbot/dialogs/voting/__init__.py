from aiogram_dialog import Dialog

from .list_nominations import nominations_window
from .list_participants import voting_window

dialog = Dialog(nominations_window, voting_window)
