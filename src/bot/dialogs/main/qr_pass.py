import os.path
import tempfile

import qrcode
from aiogram.enums import ContentType
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.api.entities import MediaAttachment
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Format
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

from src.bot import IMAGES_DIR
from src.bot.dialogs import states
from src.bot.ui import strings
from src.db import Database

QR_CODES_TEMP_DIR = tempfile.mkdtemp(prefix="ff-bot-qr-codes_")


async def qr_pass_getter(dialog_manager: DialogManager, db: Database, **kwargs):
    qr_file_path = QR_CODES_TEMP_DIR + f"/{dialog_manager.event.from_user.id}.png"
    if not os.path.exists(qr_file_path):
        qr = qrcode.QRCode(
            version=None,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=100,
        )
        qr.add_data(data=f"user {dialog_manager.event.from_user.id}")
        qr.make(fit=True)
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            embeded_image_path=IMAGES_DIR / "logo.png",
        )
        img.save(qr_file_path)
    image = MediaAttachment(
        type=ContentType.PHOTO,
        path=qr_file_path,
    )
    return {"image": image}


qr_pass_window = Window(
    Const("<b>🎫 МОЙ FAN-PASS</b>\n"),
    Const(
        "Покажи этот QR-код волонтёру или организатору, "
        "чтобы получить достижение или заработать очки.\n"
    ),
    Format("""<i>ID: {event.from_user.id}</i>"""),
    DynamicMedia("image"),
    SwitchTo(text=Const(strings.buttons.back), state=states.MAIN.MAIN, id="back"),
    state=states.MAIN.QR_PASS,
    getter=qr_pass_getter,
)
