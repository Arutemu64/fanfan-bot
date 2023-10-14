from pathlib import Path

import uvicorn
from fastapi import FastAPI
from sqladmin import Admin
from starlette.middleware.sessions import SessionMiddleware

from src.config import conf
from src.panel import engine


def create_app() -> FastAPI:
    app = FastAPI()
    app.add_middleware(SessionMiddleware, secret_key=conf.bot.secret_key)

    from src.panel.auth import AdminAuth, auth_router

    app.include_router(auth_router)

    authentication_backend = AdminAuth(secret_key=conf.bot.secret_key)
    admin = Admin(
        app,
        engine,
        base_url="/",
        title="FF-Bot",
        authentication_backend=authentication_backend,
        debug=True,
        templates_dir=Path(__file__).parent.joinpath("templates").__str__(),
    )
    from src.panel.views import views

    for view in views:
        admin.add_view(view)

    return app


if __name__ == "__main__":
    uvicorn.run("src.panel.app:create_app", reload=True, factory=True)
