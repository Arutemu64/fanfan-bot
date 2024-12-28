import json

from adaptix import Retort, name_mapping
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.pil import PilImage
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.main import QRCode

from fanfan.common.paths import COMMON_STATIC_DIR
from fanfan.core.dto.qr import QR

QRRetort = Retort(recipe=[name_mapping(QR, map={"type": "t", "data": "d"})])


def generate_img(qr_data: QR) -> PilImage:
    # We want to make encoded string as short as possible
    # Telegram QR reader also won't read some characters so no msgpack
    data = json.dumps(QRRetort.dump(qr_data), separators=(",", ":"))
    qr = QRCode(error_correction=ERROR_CORRECT_H, box_size=20)
    qr.add_data(data=data)
    qr.make(fit=True)
    return qr.make_image(
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer(),
        embeded_image_path=COMMON_STATIC_DIR.joinpath("logo.png"),
    )


def decode_qr_json(qr_data: str) -> QR:
    return QRRetort.load(json.loads(qr_data), QR)
