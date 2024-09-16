from abc import abstractmethod
from typing import Protocol


class IdProvider(Protocol):
    @abstractmethod
    def get_current_user_id(self) -> int | None:
        raise NotImplementedError
