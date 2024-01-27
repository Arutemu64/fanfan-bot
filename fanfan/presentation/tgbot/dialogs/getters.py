from typing import List

from fanfan.common.enums import UserRole


def get_roles_list() -> List:
    return list(map(lambda item: (item.value, item.label, item.label_plural), UserRole))


async def get_roles(**kwargs) -> dict:
    return {"roles": get_roles_list()}
