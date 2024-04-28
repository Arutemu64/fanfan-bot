from pydantic import BaseModel


class CreateFeedbackDTO(BaseModel):
    user_id: int
    text: str
    asap: bool = False
