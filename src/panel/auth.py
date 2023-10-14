from typing import Union

import jwt
from fastapi import APIRouter
from sqladmin.authentication import AuthenticationBackend
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from src.bot.structures import UserRole
from src.config import conf
from src.db import Database
from src.panel import engine

auth_router = APIRouter()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        return True

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request) -> Union[bool, RedirectResponse]:
        user = request.session.get("token")
        if not user:
            return RedirectResponse(request.url_for("auth"))
        return True


@auth_router.get("/auth")
async def auth(request: Request, token: str) -> Response:
    jwt_decoded = jwt.decode(
        jwt=token,
        key=conf.bot.secret_key,
        algorithms=["HS256"],
    )
    async with AsyncSession(bind=engine) as session:
        db = Database(session)
        user = await db.user.get(jwt_decoded["user_id"])
        if user.role is UserRole.ORG:
            request.session["token"] = token
            return RedirectResponse(request.url_for("admin:index"))
