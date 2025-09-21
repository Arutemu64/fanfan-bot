from dataclasses import dataclass

from fanfan.core.vo.code import CodeId
from fanfan.core.vo.ticket import TicketId


@dataclass(slots=True)
class StaffDialogData:
    new_ticket_id: TicketId | None = None
    new_ticket_code_id: CodeId | None = None
