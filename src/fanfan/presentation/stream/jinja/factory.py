from pathlib import Path
from typing import NewType

from jinja2 import Environment, FileSystemLoader

StreamJinjaEnvironment = NewType("StreamJinjaEnvironment", Environment)


def create_stream_jinja() -> StreamJinjaEnvironment:
    templates_path = Path(__file__).parent.joinpath("templates")
    environment = Environment(
        lstrip_blocks=True,
        trim_blocks=True,
        loader=FileSystemLoader(searchpath=templates_path),
        enable_async=True,
        autoescape=True,
    )
    return StreamJinjaEnvironment(environment)
