from aiogram import Router
from aiogram_dialog import Dialog

from fanfan.presentation.tgbot.dialogs.qr.handlers import qr_handlers_router
from fanfan.presentation.tgbot.dialogs.qr.main import main_qr_window

qr_router = Router(name="qr_router")

qr_dialog = Dialog(main_qr_window)

qr_router.include_routers(qr_handlers_router, qr_dialog)
