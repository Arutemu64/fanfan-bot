from functools import wraps
from typing import List, Optional

from fanfan.application.dto.user import FullUserDTO
from fanfan.application.exceptions.access import AccessDenied, TicketNotLinked
from fanfan.common.enums import UserRole


def check_permission(
    ticket_required: bool = False,
    allowed_roles: Optional[List[UserRole]] = None,
):
    """A decorator used to check user permissions. Must be used in a service
    class with self.identity attribute (FullUserDTO type).
    @param ticket_required: If True, user without a linked ticket will be denied.
    @param allowed_roles: List of allowed UserRole's, other roles will be denied.
    @raise AccessDenied:
    @return:
    """

    def check_permission_decorator(func):
        @wraps(func)
        async def check_permission_wrapper(self, *args, **kwargs):
            if not self.identity:
                raise AccessDenied
            identity: FullUserDTO = self.identity
            if ticket_required:
                if not identity.ticket:
                    raise TicketNotLinked
            if allowed_roles:
                if identity.role not in allowed_roles:
                    raise AccessDenied
            return await func(self, *args, **kwargs)

        return check_permission_wrapper

    return check_permission_decorator
