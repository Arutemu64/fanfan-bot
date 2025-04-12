import secrets
import string
from pathlib import Path

from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.main import QRCode

from fanfan.common.paths import COMMON_STATIC_DIR, QR_CODES_TEMP_DIR
from fanfan.core.models.code import CodeId


def generate_unique_code(length: int = 10) -> CodeId:
    alphabet = string.ascii_uppercase + string.digits
    return CodeId("".join(secrets.choice(alphabet) for _ in range(length)))


def get_qr_code_image(code: CodeId) -> Path:
    qr_file_path = QR_CODES_TEMP_DIR.joinpath(f"{code}.png")
    if not qr_file_path.is_file():
        qr = QRCode(error_correction=ERROR_CORRECT_H, box_size=20)
        qr.add_data(data=code)
        qr.make(fit=True)
        image = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            embeded_image_path=COMMON_STATIC_DIR.joinpath("logo.png"),
        )
        image.save(qr_file_path)
    return qr_file_path
