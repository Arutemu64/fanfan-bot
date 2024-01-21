from fanfan.common.enums import UserRole


async def get_roles(**kwargs) -> dict:
    return {
        "roles": list(
            map(lambda item: (item.value, item.label, item.label_plural), UserRole)
        )
    }
