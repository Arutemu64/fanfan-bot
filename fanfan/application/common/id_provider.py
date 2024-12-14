from abc import abstractmethod
from typing import Protocol

from fanfan.core.models.user import FullUser, UserId


class IdProvider(Protocol):
    @abstractmethod
    def get_current_user_id(self) -> UserId:
        raise NotImplementedError

    @abstractmethod
    async def get_current_user(self) -> FullUser:
        raise NotImplementedError
