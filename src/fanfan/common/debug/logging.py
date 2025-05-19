import logging
import sys

import logfire
import structlog


def setup_logging(level: int, json_logs: bool):
    renderer = (
        structlog.processors.JSONRenderer()
        if json_logs
        else structlog.dev.ConsoleRenderer()
    )

    processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.contextvars.merge_contextvars,
        structlog.stdlib.ExtraAdder(),
        structlog.dev.set_exc_info,
        structlog.processors.ExceptionPrettyPrinter(),
        structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S.%f", utc=True),
        structlog.processors.dict_tracebacks,
        logfire.StructlogProcessor(),
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
    handler.setLevel(level)
    handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.addHandler(handler)
    root_logger.setLevel(level)

    # Silence noisy loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("aiogram.event").setLevel(logging.WARNING)
    logging.getLogger("aiohttp.access").setLevel(logging.WARNING)
