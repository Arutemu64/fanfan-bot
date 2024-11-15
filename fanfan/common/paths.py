import tempfile
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent.parent
APP_DIR = ROOT_DIR / "fanfan"

COMMON_STATIC_DIR = Path(__file__).parent.joinpath("static")
JINJA_TEMPLATES_DIR = COMMON_STATIC_DIR / "templates"

TEMP_DIR = Path(tempfile.gettempdir())
TEMP_DIR.mkdir(parents=True, exist_ok=True)

QR_CODES_TEMP_DIR = TEMP_DIR.joinpath("qr_codes")
QR_CODES_TEMP_DIR.mkdir(parents=True, exist_ok=True)
