from typing import TYPE_CHECKING

from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from fanfan.application.common.id_provider import IdProvider
from fanfan.application.users.get_user_by_id import GetUserById
from fanfan.core.enums import UserRole
from fanfan.core.exceptions.users import UserNotFound

if TYPE_CHECKING:
    from dishka import AsyncContainer

auth_router = APIRouter()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        pass

    async def logout(self, request: Request) -> bool | RedirectResponse:
        request.session.clear()
        return RedirectResponse(request.url_for("auth"))

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        container: AsyncContainer = request.state.dishka_container
        id_provider: IdProvider = await container.get(IdProvider)
        if user_id := id_provider.get_current_user_id():
            get_user_by_id = await container.get(GetUserById)
            try:
                user = await get_user_by_id(user_id)
                if user.role is UserRole.ORG:
                    return True
            except UserNotFound:
                request.session.clear()
                return RedirectResponse(request.url_for("auth"))
        return RedirectResponse(request.url_for("auth"))


@auth_router.get("/admin/auth")
@inject
async def auth(
    request: Request,
    token: str,
) -> Response:
    request.session["token"] = token
    return RedirectResponse(request.url_for("admin:index"))
