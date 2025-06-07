from fanfan.core.exceptions.base import AppException


class VotesException(AppException):
    pass


class AlreadyVotedInThisNomination(VotesException):
    default_message = "Вы уже голосовали в этой номинации"


class VoteNotFound(VotesException):
    default_message = "Голос не найден"
