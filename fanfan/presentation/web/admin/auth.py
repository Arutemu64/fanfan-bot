from typing import TYPE_CHECKING

from dishka.integrations.fastapi import inject
from fastapi import APIRouter
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse, Response

from fanfan.adapters.auth.utils.token import JwtTokenProcessor
from fanfan.application.common.id_provider import IdProvider
from fanfan.core.exceptions.users import UserNotFound
from fanfan.core.models.user import UserRole

if TYPE_CHECKING:
    from dishka import AsyncContainer

admin_auth_router = APIRouter()


class AdminAuth(AuthenticationBackend):
    async def login(self, request: Request) -> bool:
        pass

    async def logout(self, request: Request) -> bool | RedirectResponse:
        request.session.clear()
        return RedirectResponse(request.url_for("auth"))

    async def authenticate(self, request: Request) -> bool | RedirectResponse:
        container: AsyncContainer = request.state.dishka_container
        id_provider: IdProvider = await container.get(IdProvider)
        try:
            user = await id_provider.get_current_user()
            if user.role is UserRole.ORG:
                # Updating token
                token_processor: JwtTokenProcessor = await container.get(
                    JwtTokenProcessor
                )
                request.session["token"] = token_processor.create_access_token(
                    user_id=user.id
                )
                return True
        except UserNotFound:
            request.session.clear()
            return RedirectResponse(request.url_for("auth"))
        return RedirectResponse(request.url_for("auth"))


@admin_auth_router.get("/admin/auth")
@inject
async def auth(
    request: Request,
    token: str,
) -> Response:
    request.session["token"] = token
    return RedirectResponse(request.url_for("admin:index"))
