import datetime

import jwt
from asyncpg.pgproto.pgproto import timedelta
from jwt import InvalidSignatureError

from fanfan.common.config import WebConfig
from fanfan.core.exceptions.auth import AuthenticationError


class JwtTokenProcessor:
    def __init__(self, config: WebConfig):
        self.config = config

    def create_access_token(self, user_id: int) -> str:
        return jwt.encode(
            payload={
                "user_id": user_id,
                "exp": datetime.datetime.now(datetime.UTC) + timedelta(minutes=15),
            },
            key=self.config.secret_key.get_secret_value(),
        )

    def validate_token(self, token: str) -> int:
        try:
            payload = jwt.decode(
                token,
                self.config.secret_key.get_secret_value(),
                algorithms=["HS256"],
            )
        except InvalidSignatureError:
            raise AuthenticationError from InvalidSignatureError

        try:
            return int(payload["user_id"])
        except ValueError:
            raise AuthenticationError from ValueError
