import enum

from pydantic import BaseModel
from qrcode.constants import ERROR_CORRECT_H
from qrcode.image.pil import PilImage
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.main import QRCode

from fanfan.common import COMMON_STATIC_DIR


class QRType(enum.StrEnum):
    ACHIEVEMENT = "achievement"


class QR(BaseModel, frozen=True):
    type: QRType
    data: str

    def generate_img(self) -> PilImage:
        qr = QRCode(
            error_correction=ERROR_CORRECT_H,
            box_size=20,
        )
        qr.add_data(data=self.model_dump_json())
        qr.make(fit=True)
        return qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            embeded_image_path=COMMON_STATIC_DIR.joinpath("logo.png"),
        )
