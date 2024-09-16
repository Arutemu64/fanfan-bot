from fanfan.application.common.id_provider import IdProvider


class RawIdProvider(IdProvider):
    def __init__(
        self,
        user_id: int | None,
    ):
        self.user_id = user_id

    def get_current_user_id(self) -> int | None:
        return self.user_id
