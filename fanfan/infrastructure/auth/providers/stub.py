from fanfan.application.common.id_provider import IdProvider


class StubIdProvider(IdProvider):
    def get_current_user_id(self) -> int | None:
        return None
