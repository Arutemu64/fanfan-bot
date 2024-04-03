from typing import Annotated, Union

import jwt
from dishka import FromDishka, make_async_container
from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from fanfan.common.enums import UserRole
from fanfan.config import conf
from fanfan.infrastructure.db.uow import UnitOfWork
from fanfan.infrastructure.di.config import ConfigProvider
from fanfan.infrastructure.di.db import DbProvider

auth_router = APIRouter()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        pass

    async def logout(self, request: Request) -> Union[bool, RedirectResponse]:
        request.session.clear()
        return RedirectResponse(request.url_for("auth"))

    async def authenticate(self, request: Request) -> Union[bool, RedirectResponse]:
        token = request.session.get("token")
        if token:
            container = make_async_container(DbProvider(), ConfigProvider())
            async with container() as request_container:
                uow = await request_container.get(UnitOfWork)
                jwt_decoded = jwt.decode(
                    jwt=token,
                    key=conf.web.secret_key.get_secret_value(),
                    algorithms=["HS256"],
                )
                user = await uow.users.get_user_by_id(jwt_decoded["user_id"])
                if user:
                    if user.role is UserRole.ORG:
                        await container.close()
                        return True
                    else:
                        pass
                else:
                    pass
            await container.close()
        request.session.clear()
        return RedirectResponse(request.url_for("auth"))


@auth_router.get("/auth")
@inject
async def auth(
    request: Request, token: str, uow: Annotated[UnitOfWork, FromDishka()]
) -> Response:
    jwt_decoded = jwt.decode(
        jwt=token,
        key=conf.web.secret_key.get_secret_value(),
        algorithms=["HS256"],
    )
    user = await uow.users.get_user_by_id(jwt_decoded["user_id"])
    if user.role is UserRole.ORG:
        request.session["token"] = token
        return RedirectResponse(request.url_for("admin:index"))
