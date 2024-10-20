import datetime

import jwt
from jwt import InvalidSignatureError

from fanfan.adapters.config_reader import WebConfig
from fanfan.core.exceptions.auth import AuthenticationError
from fanfan.core.models.user import UserId


class JwtTokenProcessor:
    def __init__(self, config: WebConfig):
        self.config = config

    def create_access_token(self, user_id: int) -> str:
        return jwt.encode(
            payload={
                "user_id": user_id,
                "exp": datetime.datetime.now(datetime.UTC)
                + datetime.timedelta(minutes=30),
            },
            key=self.config.secret_key.get_secret_value(),
        )

    def validate_token(self, token: str) -> UserId:
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key.get_secret_value(),
                algorithms=["HS256"],
            )
        except InvalidSignatureError:
            raise AuthenticationError from InvalidSignatureError

        try:
            return UserId(int(payload["user_id"]))
        except ValueError:
            raise AuthenticationError from ValueError
