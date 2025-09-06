class AppException(Exception):
    default_message = "Неизвестная ошибка"

    def __init__(self, message: str | None = None) -> None:
        super().__init__(message or self.default_message)
        self.message = message or self.default_message

    def __str__(self) -> str:
        return self.message


class AccessDenied(AppException):
    default_message = "У вас нет доступа к этой функции"
