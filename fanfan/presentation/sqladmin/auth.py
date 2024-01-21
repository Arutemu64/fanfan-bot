from typing import Union

import jwt
from fastapi import APIRouter
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from fanfan.application.services.user import UserService
from fanfan.common.enums import UserRole
from fanfan.config import conf
from fanfan.infrastructure.db.main import create_session_pool
from fanfan.infrastructure.db.uow import UnitOfWork

auth_router = APIRouter()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        print("login")
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
                    key=conf.web.secret_key.get_secret_value(),
                    algorithms=["HS256"],
                )
                uow = UnitOfWork(session)
                user = await UserService(uow).get_user_by_id(jwt_decoded["user_id"])
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
    session_pool = create_session_pool()
    jwt_decoded = jwt.decode(
        jwt=token,
        key=conf.web.secret_key.get_secret_value(),
        algorithms=["HS256"],
    )
    async with session_pool() as session:
        uow = UnitOfWork(session)
        user = await UserService(uow).get_user_by_id(jwt_decoded["user_id"])
        if user.role is UserRole.ORG:
            request.session["token"] = token
            return RedirectResponse(request.url_for("admin:index"))
