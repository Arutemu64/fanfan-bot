from aiogram.fsm.state import State, StatesGroup


class REGISTRATION(StatesGroup):
    MAIN = State()


class MAIN(StatesGroup):
    MAIN = State()
    ACTIVITIES = State()
    SCHEDULE = State()


class VOTING(StatesGroup):
    NOMINATIONS = State()
    VOTING = State()


class HELPER(StatesGroup):
    MAIN = State()


class ANNOUNCE_MODE(StatesGroup):
    MAIN = State()
    SCHEDULE = State()
    PREVIEW = State()


class ORG(StatesGroup):
    MAIN = State()
