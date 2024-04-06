import qrcode
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

from fanfan import TEMP_DIR
from fanfan.application.dto.common import QR
from fanfan.application.dto.user import FullUserDTO
from fanfan.common.enums import QRCommand
from fanfan.presentation.tgbot import UI_IMAGES_DIR
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

QR_CODES_TEMP_DIR = TEMP_DIR.joinpath("qr_codes")
QR_CODES_TEMP_DIR.mkdir(parents=True, exist_ok=True)


async def qr_pass_getter(dialog_manager: DialogManager, user: FullUserDTO, **kwargs):
    qr_data = QR(QRCommand.USER, user.ticket.id)
    qr_file_path = QR_CODES_TEMP_DIR.joinpath(f"{qr_data}.png")
    if not qr_file_path.is_file():
        qr = qrcode.QRCode(
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=20,
        )
        qr.add_data(data=qr_data)
        qr.make(fit=True)
        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            embeded_image_path=UI_IMAGES_DIR.joinpath("logo.png"),
        )
        img.save(qr_file_path)
    return {"qr_file_path": qr_file_path}


qr_pass_window = Window(
    Title(Const(strings.titles.qr_pass)),
    Const(
        "Покажи этот QR-код волонтёру или организатору, "
        "чтобы получить достижение или заработать очки.\n",
    ),
    Format("""<i>ID: {event.from_user.id}</i>"""),
    StaticMedia(path=Format("{qr_file_path}")),
    SwitchTo(text=Const(strings.buttons.back), state=states.MAIN.HOME, id="back"),
    state=states.MAIN.QR_PASS,
    getter=qr_pass_getter,
)
