class AppException(Exception):
    message = "⚠️ Неизвестная ошибка"

    def __str__(self) -> str:
        return self.message
