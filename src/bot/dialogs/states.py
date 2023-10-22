from aiogram.fsm.state import State, StatesGroup


class REGISTRATION(StatesGroup):
    MAIN = State()


class MAIN(StatesGroup):
    MAIN = State()
    ACTIVITIES = State()
    ACHIEVEMENTS = State()
    QR_PASS = State()


class SETTINGS(StatesGroup):
    MAIN = State()
    SET_ITEMS_PER_PAGE = State()


class SCHEDULE(StatesGroup):
    MAIN = State()

    ASK_MANUAL_EVENT = State()
    SWAP_EVENTS = State()
    TOGGLE_EVENT_SKIP = State()


class SUBSCRIPTIONS(StatesGroup):
    MAIN = State()
    EVENT_SELECTOR = State()
    SET_SUBSCRIPTION_COUNTER = State()


class VOTING(StatesGroup):
    NOMINATIONS = State()
    VOTING = State()


class HELPER(StatesGroup):
    MAIN = State()


class ORG(StatesGroup):
    MAIN = State()
    NEW_TICKET = State()


class USER_MANAGER(StatesGroup):
    MAIN = State()
    MANUAL_USER_SEARCH = State()

    ADD_POINTS = State()
    ADD_ACHIEVEMENT = State()

    CHANGE_ROLE = State()
