from typing import Optional

from pydantic import BaseModel


class CreateFeedbackDTO(BaseModel):
    user_id: int
    text: str
    asap: Optional[bool] = None
