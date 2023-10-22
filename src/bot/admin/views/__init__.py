from .aioparser import AioParserView
from .model_views import model_views
from .plan_parse import PlanParseView

views = [*model_views, PlanParseView, AioParserView]
