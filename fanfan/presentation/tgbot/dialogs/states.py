from aiogram.fsm.state import State, StatesGroup


class MAIN(StatesGroup):
    HOME = State()
    ACTIVITIES = State()
    ACHIEVEMENTS = State()
    QR_PASS = State()
    LINK_TICKET = State()


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
    SELECT_EVENT = State()
    SET_COUNTER = State()


class VOTING(StatesGroup):
    SELECT_NOMINATION = State()
    VOTING = State()


class HELPER(StatesGroup):
    MAIN = State()


class ORG(StatesGroup):
    MAIN = State()
    ADD_NEW_TICKET = State()


class NOTIFICATIONS(StatesGroup):
    MAIN = State()
    CREATE = State()
    DELETE = State()


class USER_MANAGER(StatesGroup):
    MAIN = State()
    MANUAL_USER_SEARCH = State()

    ADD_POINTS = State()
    ADD_ACHIEVEMENT = State()

    CHANGE_ROLE = State()
