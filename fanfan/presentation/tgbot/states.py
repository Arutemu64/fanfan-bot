from aiogram.fsm.state import State, StatesGroup


class MAIN(StatesGroup):
    HOME = State()
    LINK_TICKET = State()


class ACTIVITIES(StatesGroup):
    SELECT_ACTIVITY = State()
    ACTIVITY_INFO = State()


class ACHIEVEMENTS(StatesGroup):
    MAIN = State()


class SETTINGS(StatesGroup):
    MAIN = State()
    SET_ITEMS_PER_PAGE = State()


class SCHEDULE(StatesGroup):
    MAIN = State()
    SUBSCRIPTIONS = State()


class EVENT_DETAILS(StatesGroup):
    MAIN = State()
    MOVE_EVENT = State()
    SET_SUBSCRIPTION_COUNTER = State()


class VOTING(StatesGroup):
    SELECT_NOMINATION = State()
    VOTING = State()


class HELPER(StatesGroup):
    MAIN = State()


class ORG(StatesGroup):
    MAIN = State()
    ADD_NEW_TICKET = State()


class DELIVERIES(StatesGroup):
    MAIN = State()
    CREATE = State()
    DELETE = State()


class USER_MANAGER(StatesGroup):
    MAIN = State()
    MANUAL_USER_SEARCH = State()
    CHANGE_ROLE = State()


class FEEDBACK(StatesGroup):
    MAIN = State()
