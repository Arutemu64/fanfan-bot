import logging

from pydantic import BaseModel, SecretStr


class DebugConfig(BaseModel):
    enabled: bool = True
    test_mode: bool = False

    logging_level: int = logging.DEBUG
    json_logs: bool = False

    logfire_token: SecretStr | None = None
