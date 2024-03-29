from pathlib import Path

import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from sqlalchemy.ext.asyncio import async_sessionmaker

from fanfan.config import conf


def setup_admin(app: FastAPI, session_pool: async_sessionmaker) -> None:
    from fanfan.presentation.sqladmin.auth import AdminAuth, auth_router

    app.include_router(auth_router)
    authentication_backend = AdminAuth(
        secret_key=conf.web.secret_key.get_secret_value()
    )

    admin = Admin(
        app=app,
        session_maker=session_pool,
        title="FF-Bot",
        authentication_backend=authentication_backend,
        debug=conf.debug.enabled,
        templates_dir=Path(__file__).parent.joinpath("templates").__str__(),
    )

    from fanfan.presentation.sqladmin.views import views

    for v in views:
        admin.add_view(v)


if __name__ == "__main__":
    uvicorn.run("src.panel.app:create_app", reload=True, factory=True)
