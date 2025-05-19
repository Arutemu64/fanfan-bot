from abc import abstractmethod
from typing import Protocol

from fanfan.core.models.user import UserData
from fanfan.core.vo.user import UserId


class IdProvider(Protocol):
    @abstractmethod
    def is_system(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_current_user_id(self) -> UserId:
        raise NotImplementedError

    @abstractmethod
    async def get_user_data(self) -> UserData:
        raise NotImplementedError
