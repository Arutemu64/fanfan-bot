from fanfan.application.exceptions import ServiceError


class VotingServiceError(ServiceError):
    message = "⚠️ Произошла неизвестная ошибка в сервисе голосования"


class VotingDisabled(VotingServiceError):
    message = "⚠️ Голосование сейчас отключено"


class AlreadyVotedInThisNomination(VotingServiceError):
    message = "⚠️ Вы уже голосовали в этой номинации"


class VotingServiceNotAllowed(VotingServiceError):
    message = "⚠️ Голосование недоступно"


class VoteNotFound(VotingServiceError):
    message = "⚠️ Голос не найден"
