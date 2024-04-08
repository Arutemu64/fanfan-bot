from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format

from fanfan.application.dto.qr import QR
from fanfan.application.dto.user import FullUserDTO
from fanfan.common import TEMP_DIR
from fanfan.common.enums import QRType
from fanfan.presentation.tgbot.dialogs import states
from fanfan.presentation.tgbot.dialogs.widgets import Title
from fanfan.presentation.tgbot.ui import strings

QR_CODES_TEMP_DIR = TEMP_DIR.joinpath("qr_codes")
QR_CODES_TEMP_DIR.mkdir(parents=True, exist_ok=True)


async def qr_pass_getter(dialog_manager: DialogManager, user: FullUserDTO, **kwargs):
    qr = QR(type=QRType.USER, data=str(user.id))
    qr_file_path = QR_CODES_TEMP_DIR.joinpath(f"{hash(qr)}.png")
    if not qr_file_path.is_file():
        qr.generate_img().save(qr_file_path)
    return {"qr_file_path": qr_file_path}


qr_pass_window = Window(
    Title(Const(strings.titles.qr_pass)),
    Const(
        "Это твой FAN-Pass, покажи его волонтёру, "
        "чтобы он смог проверить полученные тобой достижения.",
    ),
    Const(" "),
    Format("""<i>ID: {event.from_user.id}</i>"""),
    StaticMedia(path=Format("{qr_file_path}")),
    SwitchTo(text=Const(strings.buttons.back), state=states.MAIN.HOME, id="back"),
    state=states.MAIN.QR_PASS,
    getter=qr_pass_getter,
)
