import os
import tomllib
from pathlib import Path

from fanfan.adapters.config.models import Configuration
from fanfan.common.paths import ROOT_DIR

DEFAULT_CONFIG_PATH = ROOT_DIR.joinpath("config/config.toml")


def get_config() -> Configuration:
    # Pick config path
    if config_path := os.getenv("CONFIG_PATH"):
        path = Path(config_path)
    else:
        path = DEFAULT_CONFIG_PATH
    # Load config
    with path.open("rb") as cfg:
        cfg_dict = tomllib.load(cfg)
    # Read additional parameters from env
    cfg_dict.update(env_name=os.getenv("ENV_NAME", default="dev"))
    return Configuration.model_validate(cfg_dict)
