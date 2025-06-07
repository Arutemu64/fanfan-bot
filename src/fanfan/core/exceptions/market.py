from fanfan.core.exceptions.base import AppException


class MarketException(AppException):
    pass


class MarketNotFound(MarketException):
    user_message = "Магазин не найден"


class ProductNotFound(MarketException):
    user_message = "Товар не найден"


class MarketNameTooLong(MarketException):
    user_message = "Слишком длинное название магазина"


class MarketDescTooLong(MarketException):
    user_message = "Слишком длинное описание"


class ProductNameTooLong(MarketException):
    user_message = "Слишком длинное название товара"


class ProductDescTooLong(MarketException):
    user_message = "Слишком длинное описание товара"


class NegativeProductPrice(MarketException):
    user_message = "Стоимость не может быть отрицательная"


class UserIsAlreadyMarketManager(MarketException):
    user_message = "Пользователь уже является управляющим магазина"
