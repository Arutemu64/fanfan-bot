import os

from fanfan.adapters.config.models import EnvConfig


def get_config() -> EnvConfig:
    return EnvConfig(_env_file=os.getenv("ENV_FILE"))
