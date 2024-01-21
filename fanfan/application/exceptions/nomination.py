from fanfan.application.exceptions import ServiceError


class NominationServiceError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе номинаций"


class NominationNotFound(NominationServiceError):
    message = "⚠️ Номинация не найдена"


class NominationAlreadyExist(NominationServiceError):
    message = "⚠️ Номинация уже существует"
