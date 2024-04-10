from typing import NamedTuple


class Plurals(NamedTuple):
    one: str
    three: str
    five: str


SECONDS_PLURALS = Plurals("секунду", "секунды", "секунд")
NOTIFICATIONS_PLURALS = Plurals("уведомление", "уведомления", "уведомлений")


def pluralize(value: int, strings: Plurals) -> str:
    if (value % 10 == 1) and (value % 100 != 11):
        # Пример: 1 секунду
        return strings.one
    elif (2 <= value % 10 <= 4) and (value % 100 < 10 or value % 100 >= 20):
        # Пример: 3 секунды
        return strings.three
    else:
        # Пример: 5 секунд
        return strings.five
