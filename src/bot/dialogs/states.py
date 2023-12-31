from aiogram.fsm.state import State, StatesGroup


class MAIN(StatesGroup):
    MAIN = State()
    ACTIVITIES = State()
    ACHIEVEMENTS = State()
    QR_PASS = State()


class LINK_TICKET(StatesGroup):
    ASK_TICKET_NUMBER = State()


class SETTINGS(StatesGroup):
    MAIN = State()
    SET_ITEMS_PER_PAGE = State()


class SCHEDULE(StatesGroup):
    MAIN = State()

    ASK_MANUAL_EVENT = State()
    SWAP_EVENTS = State()
    TOGGLE_EVENT_SKIP = State()

    SUBSCRIPTIONS_MAIN = State()
    SUBSCRIPTIONS_EVENT_SELECTOR = State()
    SUBSCRIPTIONS_SET_COUNTER = State()


class VOTING(StatesGroup):
    NOMINATIONS = State()
    VOTING = State()


class HELPER(StatesGroup):
    MAIN = State()


class ORG(StatesGroup):
    MAIN = State()
    NEW_TICKET = State()

    CREATE_NOTIFICATION = State()
    CONFIRM_NOTIFICATION = State()


class USER_MANAGER(StatesGroup):
    MAIN = State()
    MANUAL_USER_SEARCH = State()

    ADD_POINTS = State()
    ADD_ACHIEVEMENT = State()

    CHANGE_ROLE = State()
