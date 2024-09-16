from fanfan.core.exceptions.base import AppException


class VotesException(AppException):
    message = "⚠️ Произошла неизвестная ошибка в сервисе голосования"


class VotingDisabled(VotesException):
    message = "⚠️ Голосование сейчас отключено"


class AlreadyVotedInThisNomination(VotesException):
    message = "⚠️ Вы уже голосовали в этой номинации"


class VotingServiceNotAllowed(VotesException):
    message = "⚠️ Голосование недоступно"


class VoteNotFound(VotesException):
    message = "⚠️ Голос не найден"
