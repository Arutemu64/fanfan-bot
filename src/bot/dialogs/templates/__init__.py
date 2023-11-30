from pathlib import Path

TEMPLATES_DIR = Path(__file__).parent


def load_template(template_filename: str) -> str:
    return TEMPLATES_DIR.joinpath(template_filename).read_text(encoding="utf-8")


schedule_list = load_template("schedule_list.jinja2")
subscriptions_list = load_template("subscriptions_list.jinja2")
achievements_list = load_template("achievements_list.jinja2")
voting_list = load_template("voting_list.jinja2")
global_announcement = load_template("global_announcement.jinja2")
subscription_notification = load_template("subscription_notification.jinja2")
