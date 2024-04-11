class ServiceError(Exception):
    message = "⚠️ Неизвестная сервисная ошибка"

    def __str__(self):
        return self.message


class UnhandledError(ServiceError):
    def __init__(self, exception: Exception, user_id: int):
        self.message = (
            f"⚠️ Возникла необработанная ошибка ({type(exception).__name__})\n\n"
            "Пожалуйста, сообщите о ней @Arutemu64 (не забудьте "
            f"также назвать свой ID <code>{user_id}</code>) "
            "и попробуйте перезапустить бота командой /start"
        )
