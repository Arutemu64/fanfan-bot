from dataclasses import dataclass

from fanfan.core.vo.transaction import TransactionId
from fanfan.core.vo.user import UserId


@dataclass(slots=True, kw_only=True)
class Transaction:
    id: TransactionId | None = None
    points: int
    comment: str

    to_user_id: UserId
    from_user_id: UserId
