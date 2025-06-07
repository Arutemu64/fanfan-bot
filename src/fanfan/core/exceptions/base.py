class AppException(Exception):
    user_message = "Неизвестная ошибка"

    def __init__(self, user_message: str) -> None:
        self.user_message = user_message

    def __str__(self) -> str:
        return self.user_message


class AccessDenied(AppException):
    user_message = "У вас нет доступа к этой функции"
