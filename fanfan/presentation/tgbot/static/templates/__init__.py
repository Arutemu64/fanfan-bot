from fanfan.presentation.tgbot import JINJA_TEMPLATES_DIR


def load_template(template_filename: str) -> str:
    return JINJA_TEMPLATES_DIR.joinpath(template_filename).read_text(encoding="utf-8")


schedule_list = load_template("schedule_list.jinja2")
subscriptions_list = load_template("subscriptions_list.jinja2")
achievements_list = load_template("achievements_list.jinja2")
voting_list = load_template("voting_list.jinja2")
