from dataclasses import dataclass

from fanfan.core.vo.user import UserId


@dataclass(slots=True)
class UserManagerDialogData:
    selected_user_id: UserId

    # Adding points
    points: int | None = None
    comment: str | None = None

    # Personal message
    message_text: str | None = None
