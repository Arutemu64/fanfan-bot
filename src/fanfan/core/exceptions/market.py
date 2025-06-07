from fanfan.core.exceptions.base import AppException


class MarketException(AppException):
    pass


class MarketNotFound(MarketException):
    default_message = "Магазин не найден"


class ProductNotFound(MarketException):
    default_message = "Товар не найден"


class MarketNameTooLong(MarketException):
    default_message = "Слишком длинное название магазина"


class MarketDescTooLong(MarketException):
    default_message = "Слишком длинное описание"


class ProductNameTooLong(MarketException):
    default_message = "Слишком длинное название товара"


class ProductDescTooLong(MarketException):
    default_message = "Слишком длинное описание товара"


class NegativeProductPrice(MarketException):
    default_message = "Стоимость не может быть отрицательная"


class UserIsAlreadyMarketManager(MarketException):
    default_message = "Пользователь уже является управляющим магазина"
