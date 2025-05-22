from pydantic import BaseModel, SecretStr


class TCloudConfig(BaseModel):
    api_key: SecretStr
    participant_event_id: str | None = None
