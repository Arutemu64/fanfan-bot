from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.auth import NoUserContextError
from fanfan.core.models.user import UserFull, UserId


class SystemIdProvider(IdProvider):
    """
    SystemIdProvider is an implementation of IdProvider used internally
    for services that has no real user identity (i.e. scheduler) behind.
    Interactors that might potentially be used by such services
    must implement explicit check for SystemIdProvider type
    and handle the case accordingly, otherwise NoUserContextError
    will be raised at some point.
    There are probably better ways to handle that, but I'm dumb and lazy.
    """

    def get_current_user_id(self) -> UserId:
        raise NoUserContextError

    async def get_current_user(self) -> UserFull:
        raise NoUserContextError
