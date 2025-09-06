from fanfan.core.constants.permissions import PermissionObjectTypes, Permissions
from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.market import Market
from fanfan.core.models.user import User
from fanfan.core.services.permissions import UserPermissionService


class MarketService:
    def __init__(self, user_perm_service: UserPermissionService):
        self.user_perm_service = user_perm_service

    async def ensure_user_can_manage_market(self, market: Market, user: User):
        user_perm = await self.user_perm_service.get_user_permission(
            perm_name=Permissions.CAN_MANAGE_MARKET,
            user_id=user.id,
            object_type=PermissionObjectTypes.MARKET,
            object_id=market.id,
        )
        if not user_perm:
            reason = "У вас нет прав для редактирования этого магазина"
            raise AccessDenied(reason)
