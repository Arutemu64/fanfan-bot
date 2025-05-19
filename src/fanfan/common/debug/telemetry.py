import logfire


def setup_telemetry(
    service_name: str, environment: str, logfire_token: str | None
) -> None:
    if logfire_token:
        # Setup Logfire
        logfire.configure(
            token=logfire_token,
            service_name=service_name,
            environment=environment,
            console=False,
        )
