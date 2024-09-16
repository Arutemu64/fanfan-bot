from starlette.requests import Request

from fanfan.application.common.id_provider import IdProvider
from fanfan.infrastructure.auth.utils.token import JwtTokenProcessor


class WebIdProvider(IdProvider):
    def __init__(self, request: Request, token_processor: JwtTokenProcessor):
        self.request = request
        self.token_processor = token_processor

    def get_current_user_id(self) -> int | None:
        if token := self.request.session.get("token"):
            return self.token_processor.validate_token(token)
        return None
