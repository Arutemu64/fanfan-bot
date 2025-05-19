from fanfan.core.exceptions.base import AppException
from fanfan.core.vo.participant import ParticipantId


class ParticipantsException(AppException):
    pass


class ParticipantNotFound(ParticipantsException):
    def __init__(self, participant_id: ParticipantId):
        self.message = f"⚠️ Участник {participant_id} не найден"
