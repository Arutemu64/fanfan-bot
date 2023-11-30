from pathlib import Path

BOT_ROOT_DIR = Path(__file__).parent
UI_DIR = BOT_ROOT_DIR.joinpath("ui")
IMAGES_DIR = UI_DIR.joinpath("images")
STATIC_DIR = BOT_ROOT_DIR.joinpath("static")
