class ServiceError(Exception):
    message = "⚠️ Неизвестная сервисная ошибка"

    def __repr__(self) -> str:
        return self.message


class UnhandledError(ServiceError):
    def __init__(self, exception_name: str, user_id: int):
        self.message = (
            f"⚠️ Возникла необработанная ошибка ({exception_name})\n\n"
            "Пожалуйста, сообщите о ней @Arutemu64 (не забудьте "
            f"также назвать свой ID <code>{user_id}</code>) "
            "и попробуйте перезапустить бота командой /start"
        )
