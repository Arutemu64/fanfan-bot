from typing import TypedDict

from src.bot.structures import UserRole


class UserData(TypedDict):
    role: UserRole
    items_per_page: int
