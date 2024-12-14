import json

from adaptix import Retort
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.pil import PilImage
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.main import QRCode

from fanfan.common.paths import COMMON_STATIC_DIR
from fanfan.core.models.qr import QR


def generate_img(qr_data: QR) -> PilImage:
    qr = QRCode(
        error_correction=ERROR_CORRECT_H,
        box_size=20,
    )
    qr.add_data(data=json.dumps(Retort().dump(qr_data)))
    qr.make(fit=True)
    return qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        embeded_image_path=COMMON_STATIC_DIR.joinpath("logo.png"),
    )
