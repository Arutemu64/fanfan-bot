from aiogram.fsm.state import State, StatesGroup


class MAIN(StatesGroup):
    MAIN = State()


class HELPER(StatesGroup):
    MAIN = State()


class VOTING(StatesGroup):
    NOMINATIONS = State()
    VOTING = State()


class SCHEDULE(StatesGroup):
    MAIN = State()


class ANNOUNCE_MODE(StatesGroup):
    MAIN = State()
    PREVIEW = State()


class ORG(StatesGroup):
    MAIN = State()


class ACTIVITIES(StatesGroup):
    MAIN = State()
