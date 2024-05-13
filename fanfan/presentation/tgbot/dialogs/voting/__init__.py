from aiogram_dialog import Dialog

from .windows import nominations_window, voting_window

dialog = Dialog(nominations_window, voting_window)
