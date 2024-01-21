import tempfile
from pathlib import Path

TEMP_DIR = Path(tempfile.gettempdir())
TEMP_DIR.mkdir(parents=True, exist_ok=True)
