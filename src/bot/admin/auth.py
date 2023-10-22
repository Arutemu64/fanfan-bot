from typing import Union

import jwt
from fastapi import APIRouter
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import async_sessionmaker
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from src.bot.structures import UserRole
from src.config import conf
from src.db import Database
from src.db.database import create_session_pool

auth_router = APIRouter()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        return True

    async def logout(self, request: Request) -> Union[bool, RedirectResponse]:
        request.session.clear()
        return RedirectResponse(request.url_for("auth"))

    async def authenticate(self, request: Request) -> Union[bool, RedirectResponse]:
        token = request.session.get("token")
        if token:
            session_pool = create_session_pool()
            async with session_pool() as session:
                jwt_decoded = jwt.decode(
                    jwt=token,
                    key=conf.web.secret_key,
                    algorithms=["HS256"],
                )
                db = Database(session)
                user = await db.user.get(jwt_decoded["user_id"])
                if user:
                    if user.role is UserRole.ORG:
                        return True
                    else:
                        pass
                else:
                    pass
        request.session.clear()
        return RedirectResponse(request.url_for("auth"))


@auth_router.get("/auth")
async def auth(request: Request, token: str) -> Response:
    session_pool: async_sessionmaker = request.app.state.session_pool
    jwt_decoded = jwt.decode(
        jwt=token,
        key=conf.web.secret_key,
        algorithms=["HS256"],
    )
    async with session_pool() as session:
        db = Database(session)
        user = await db.user.get(jwt_decoded["user_id"])
        if user.role is UserRole.ORG:
            request.session["token"] = token
            return RedirectResponse(request.url_for("admin:index"))
