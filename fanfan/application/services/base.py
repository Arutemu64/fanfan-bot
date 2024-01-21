from typing import Optional

from fanfan.application.dto.user import FullUserDTO
from fanfan.infrastructure.db import UnitOfWork


class BaseService:
    def __init__(self, uow: UnitOfWork, identity: Optional[FullUserDTO] = None):
        self.uow = uow
        self.identity = identity
