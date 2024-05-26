from typing import Optional

from pydantic import BaseModel, ConfigDict

from fanfan.common.enums import UserRole


class CreateTicketDTO(BaseModel):
    id: str
    role: UserRole


class TicketDTO(BaseModel):
    model_config = ConfigDict(from_attributes=True, frozen=True)

    id: str
    role: UserRole
    used_by_id: Optional[int]
    issued_by_id: Optional[int]
