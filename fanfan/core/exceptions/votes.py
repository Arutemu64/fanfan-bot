from fanfan.core.exceptions.access import AccessDenied
from fanfan.core.exceptions.base import AppException


class VotesException(AppException):
    message = "⚠️ Произошла неизвестная ошибка в сервисе голосования"


class VotingDisabled(VotesException, AccessDenied):
    message = "⚠️ Голосование сейчас отключено"


class AlreadyVotedInThisNomination(VotesException, AccessDenied):
    message = "⚠️ Вы уже голосовали в этой номинации"


class VotingServiceNotAllowed(VotesException):
    message = "⚠️ Голосование недоступно"


class VoteNotFound(VotesException):
    message = "⚠️ Голос не найден"
