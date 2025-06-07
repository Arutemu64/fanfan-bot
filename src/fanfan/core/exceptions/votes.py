from fanfan.core.exceptions.base import AppException


class VotesException(AppException):
    pass


class AlreadyVotedInThisNomination(VotesException):
    user_message = "Вы уже голосовали в этой номинации"


class VoteNotFound(VotesException):
    user_message = "Голос не найден"
