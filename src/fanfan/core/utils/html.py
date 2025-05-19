import nh3

ALLOWED_TAGS = {
    "a",
    "b",
    "strong",
    "i",
    "em",
    "s",
    "strike",
    "del",
    "u",
    "ins",
    "span",
    "tg-spoiler",
    "pre",
    "code",
}


def sanitize_html(text: str) -> str:
    return nh3.clean(text, tags=ALLOWED_TAGS)
