from aiogram.fsm.state import State, StatesGroup


class Achievements(StatesGroup):
    LIST_ACHIEVEMENTS = State()


class Activities(StatesGroup):
    LIST_ACTIVITIES = State()
    VIEW_ACTIVITY = State()


class Feedback(StatesGroup):
    SEND_FEEDBACK = State()


class Main(StatesGroup):
    HOME = State()
    LINK_TICKET = State()
    QR_CODE = State()


class Mailing(StatesGroup):
    MAIN = State()
    CREATE_MAILING = State()
    FIND_MAILING = State()
    MAILING_INFO = State()


class Schedule(StatesGroup):
    MAIN = State()
    SUBSCRIPTIONS = State()

    EVENT_DETAILS = State()
    MOVE_EVENT = State()
    ADD_SUBSCRIPTION = State()


class Settings(StatesGroup):
    MAIN = State()
    SET_ITEMS_PER_PAGE = State()


class UserManager(StatesGroup):
    USER_INFO = State()
    MANUAL_USER_SEARCH = State()
    CHANGE_ROLE = State()
    SEND_MESSAGE = State()

    # Adding points
    SET_POINTS = State()
    SET_COMMENT = State()
    PREVIEW_ADD_POINTS = State()


class Voting(StatesGroup):
    LIST_NOMINATIONS = State()
    ADD_VOTE = State()


class Quest(StatesGroup):
    MAIN = State()


class InlineQuerySearch(StatesGroup):
    EVENTS = State()
    VOTING_PARTICIPANTS = State()


class TestMode(StatesGroup):
    MAIN = State()


class Staff(StatesGroup):
    MAIN = State()

    CREATE_TICKET_PICK_ROLE = State()
    CREATE_TICKET_RESULT = State()
