import logging
import sys

import structlog

from fanfan.adapters.config_reader import get_config


def setup_logging():
    config = get_config()

    renderer = structlog.dev.ConsoleRenderer()

    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.ExtraAdder(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=True),
        structlog.processors.dict_tracebacks,
    ]

    logging_processors = [
        structlog.stdlib.ProcessorFormatter.remove_processors_meta,
        renderer,
    ]

    formatter = structlog.stdlib.ProcessorFormatter(
        foreign_pre_chain=processors,
        processors=logging_processors,
    )

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.set_name("default")
    handler.setLevel(config.debug.logging_level)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(config.debug.logging_level)

    # Silence aiogram
    aiogram_event_logger = logging.getLogger("aiogram.event")
    aiogram_event_logger.setLevel(logging.WARNING)
