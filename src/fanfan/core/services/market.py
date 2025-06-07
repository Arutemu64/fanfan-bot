from fanfan.core.exceptions.base import AccessDenied
from fanfan.core.models.market import Market
from fanfan.core.models.user import User


class MarketService:
    @staticmethod
    def ensure_user_can_manage_market(market: Market, manager: User):
        if manager.id not in market.manager_ids:
            reason = "У вас нет прав для редактирования этого магазина"
            raise AccessDenied(reason)
