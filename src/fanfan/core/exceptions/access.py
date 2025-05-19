from fanfan.core.exceptions.base import AppException


class AccessDenied(AppException):
    message = "⚠️ У вас нет доступа к этой функции"
