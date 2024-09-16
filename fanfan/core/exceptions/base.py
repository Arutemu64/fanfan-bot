class AppException(Exception):
    message = "⚠️ Неизвестная ошибка"

    def __str__(self) -> str:
        return self.message


class UnhandledException(AppException):
    def __init__(self, exception: Exception, user_id: int) -> None:
        self.message = (
            f"⚠️ Возникла необработанная ошибка ({type(exception).__name__})\n\n"
            "Пожалуйста, сообщите о ней @Arutemu64 (не забудьте "
            f"также назвать свой ID <code>{user_id}</code>) "
            "и попробуйте перезапустить бота командой /start"
        )
