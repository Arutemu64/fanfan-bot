from src.bot.dialogs import states
from src.bot.dialogs.widgets.schedule import get_schedule_widget

schedule = get_schedule_widget(state=states.MAIN.SCHEDULE, back_to=states.MAIN.MAIN)
