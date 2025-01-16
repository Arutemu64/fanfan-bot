import sentry_sdk

from fanfan.adapters.config.models import Configuration


def setup_telemetry(config: Configuration) -> None:
    # Setup Sentry
    if config.debug.sentry_enabled:
        sentry_sdk.init(
            dsn=config.debug.sentry_dsn,
            environment=config.env_name,
            traces_sample_rate=1.0,
            profiles_sample_rate=1.0,
        )
