from fanfan.core.exceptions.base import AppException


class MarketException(AppException):
    message = "⚠️ Неизвестная ошибка в сервисе маркетплейса"


class MarketNotFound(MarketException):
    message = "⚠️ Магазин не найден"


class ProductNotFound(MarketException):
    message = "⚠️ Товар не найден"


class MarketNameTooLong(MarketException):
    message = "⚠️ Слишком длинное название магазина"


class MarketDescTooLong(MarketException):
    message = "⚠️ Слишком длинное описание"


class ProductNameTooLong(MarketException):
    message = "⚠️ Слишком длинное название товара"


class ProductDescTooLong(MarketException):
    message = "⚠️ Слишком длинное описание товара"


class NegativeProductPrice(MarketException):
    message = "⚠️ Стоимость не может быть отрицательная"


class UserIsAlreadyMarketManager(MarketException):
    message = "⚠️ Пользователь уже является управляющим магазина"
