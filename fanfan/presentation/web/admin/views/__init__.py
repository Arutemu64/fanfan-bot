from .models import model_views
from .parse_schedule import ParseScheduleView
from .parse_tickets import ParseTicketsView

views = [*model_views, ParseScheduleView, ParseTicketsView]
