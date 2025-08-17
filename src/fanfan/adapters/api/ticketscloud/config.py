from pydantic import BaseModel, SecretStr

from fanfan.core.vo.user import UserRole


class TCloudConfig(BaseModel):
    api_key: SecretStr
    event_ids: dict[str, UserRole]
