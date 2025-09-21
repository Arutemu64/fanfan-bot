from abc import abstractmethod
from typing import Protocol

from fanfan.core.models.user import User


class IdProvider(Protocol):
    @abstractmethod
    async def get_current_user(self) -> User:
        raise NotImplementedError
