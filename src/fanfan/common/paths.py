import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
APP_DIR = ROOT_DIR / "fanfan"

COMMON_STATIC_DIR = Path(__file__).parent.joinpath("static")

TEMP_DIR = Path(tempfile.gettempdir())
TEMP_DIR.mkdir(parents=True, exist_ok=True)

QR_CODES_TEMP_DIR = TEMP_DIR.joinpath("qr_codes")
QR_CODES_TEMP_DIR.mkdir(parents=True, exist_ok=True)
