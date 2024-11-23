from aiogram.fsm.state import State, StatesGroup


class Achievements(StatesGroup):
    list_achievements = State()


class Activities(StatesGroup):
    list_activities = State()
    view_activity = State()


class Feedback(StatesGroup):
    send_feedback = State()


class Helper(StatesGroup):
    main = State()


class Main(StatesGroup):
    home = State()
    link_ticket = State()


class Org(StatesGroup):
    main = State()
    tasks = State()
    input_task_cron = State()
    add_ticket = State()


class Mailing(StatesGroup):
    main = State()
    create_mailing = State()
    find_mailing = State()
    mailing_info = State()
    delete_mailing = State()


class Schedule(StatesGroup):
    main = State()
    subscriptions = State()

    event_details = State()
    move_event = State()
    add_subscription = State()


class EventDetails(StatesGroup):
    main = State()
    move_event = State()
    add_subscription = State()


class Settings(StatesGroup):
    main = State()
    set_items_per_page = State()


class UserManager(StatesGroup):
    user_info = State()
    manual_user_search = State()
    change_role = State()
    add_points = State()


class Voting(StatesGroup):
    list_nominations = State()
    add_vote = State()


class Quest(StatesGroup):
    main = State()


class InlineQuerySearch(StatesGroup):
    events = State()
    voting_participants = State()


class TestMode(StatesGroup):
    main = State()
