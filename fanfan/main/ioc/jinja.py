from dishka import Provider, Scope, provide
from jinja2 import Environment, FileSystemLoader

from fanfan.common.paths import JINJA_TEMPLATES_DIR


class JinjaProvider(Provider):
    scope = Scope.APP

    @provide
    def provide_jinja_env(self) -> Environment:
        return Environment(
            lstrip_blocks=True,
            trim_blocks=True,
            loader=FileSystemLoader(searchpath=JINJA_TEMPLATES_DIR),
            enable_async=True,
            autoescape=True,
        )
