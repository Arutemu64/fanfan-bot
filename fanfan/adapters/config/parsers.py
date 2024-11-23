import os

from fanfan.adapters.config.models import Configuration


def get_config() -> Configuration:
    return Configuration(_env_file=os.getenv("ENV_FILE"))
