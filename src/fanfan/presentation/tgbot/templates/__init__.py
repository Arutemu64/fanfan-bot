from pathlib import Path


def load_template(template_filename: str) -> str:
    return Path(__file__).parent.joinpath(template_filename).read_text(encoding="utf-8")


achievements_list = load_template("achievements_list.jinja2")
schedule_list = load_template("schedule_list.jinja2")
selected_event_info = load_template("selected_event_info.jinja2")
subscriptions_list = load_template("subscriptions_list.jinja2")
voting_list = load_template("voting_list.jinja2")
rating_list = load_template("rating_list.jinja2")
product_list = load_template("products_list.jinja2")
participants_list = load_template("participants_list.jinja2")
view_participant = load_template("view_participant.jinja2")
