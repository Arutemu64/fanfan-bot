from fanfan.application.exceptions import ServiceError


class ParticipantServiceError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе участников"


class ParticipantNotFound(ParticipantServiceError):
    message = "⚠️ Участник не найден"
