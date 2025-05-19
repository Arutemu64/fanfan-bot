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

    USER_SETTINGS = State()
    SET_ITEMS_PER_PAGE = State()

    ORG_SETTINGS = State()
    DEV_SETTINGS = State()
    FEST_SETTINGS = State()


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
    RATING = State()


class InlineQuerySearch(StatesGroup):
    EVENTS = State()
    VOTING_PARTICIPANTS = State()


class Staff(StatesGroup):
    MAIN = State()

    CREATE_MARKET = State()

    CREATE_TICKET_PICK_ROLE = State()
    CREATE_TICKET_RESULT = State()


class Marketplace(StatesGroup):
    LIST_MARKETS = State()
    VIEW_MARKET = State()
    EDIT_MARKET_NAME = State()
    EDIT_MARKET_DESCRIPTION = State()
    EDIT_MARKET_IMAGE = State()
    ADD_MANAGER = State()

    LIST_PRODUCTS = State()
    VIEW_PRODUCT = State()
    EDIT_PRODUCT_NAME = State()
    EDIT_PRODUCT_DESCRIPTION = State()
    EDIT_PRODUCT_PRICE = State()
    EDIT_PRODUCT_IMAGE = State()
    CONFIRM_PRODUCT_DELETE = State()
