from fanfan.core.exceptions.base import AppException


class PermissionsException(AppException):
    pass


class PermissionNotFound(PermissionsException):
    default_message = "Разрешение не найдено"


class UserAlreadyHasPermission(PermissionsException):
    default_message = "У пользователя уже есть это разрешение"
