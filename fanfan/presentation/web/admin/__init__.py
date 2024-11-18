from pathlib import Path

from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import async_sessionmaker

from fanfan.adapters.config.models import Configuration
from fanfan.presentation.web.admin.auth import AdminAuth


def setup_admin(
    app: FastAPI, config: Configuration, session_pool: async_sessionmaker
) -> None:
    admin = Admin(
        app=app,
        session_maker=session_pool,
        base_url=f"{config.web.path}/admin",
        title="FF-Bot",
        authentication_backend=AdminAuth(
            secret_key=config.web.secret_key.get_secret_value(),
        ),
        debug=config.debug.enabled,
        templates_dir=Path(__file__).parent.joinpath("templates").__str__(),
    )

    from fanfan.presentation.web.admin.views import views

    for v in views:
        admin.add_view(v)
