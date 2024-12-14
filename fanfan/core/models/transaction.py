from dataclasses import dataclass
from typing import NewType

from fanfan.core.models.user import UserId

TransactionId = NewType("TransactionId", int)


@dataclass(slots=True, kw_only=True)
class Transaction:
    id: TransactionId | None = None
    points: int
    comment: str

    to_user_id: UserId
    from_user_id: UserId
