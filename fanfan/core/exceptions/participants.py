from fanfan.core.exceptions.base import AppException


class ParticipantsException(AppException):
    pass


class ParticipantNotFound(ParticipantsException):
    message = "⚠️ Участник не найден"
