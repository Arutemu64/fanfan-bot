from aiogram.fsm.state import State, StatesGroup


class REGISTRATION(StatesGroup):
    MAIN = State()


class MAIN(StatesGroup):
    MAIN = State()
    ACTIVITIES = State()
    HELPER = State()
    ORG = State()


class SCHEDULE(StatesGroup):
    MAIN = State()
    ASK_MANUAL_EVENT = State()
    SWAP_EVENTS = State()
    ASK_SUBSCRIPTION_COUNTER = State()


class VOTING(StatesGroup):
    NOMINATIONS = State()
    VOTING = State()


class ORG(StatesGroup):
    MAIN = State()
    NEW_TICKET = State()
    ASK_USERNAME = State()
    USER_EDITOR = State()
    CHANGE_ROLE = State()
