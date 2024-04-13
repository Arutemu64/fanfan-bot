from pydantic import BaseModel


class CreateFeedbackDTO(BaseModel):
    user_id: int
    text: str
    contact_agreement: bool
    asap: bool = False
