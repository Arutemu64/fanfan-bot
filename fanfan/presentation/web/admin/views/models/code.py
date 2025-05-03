from sqladmin import ModelView, action
from starlette.requests import Request
from starlette.responses import FileResponse

from fanfan.adapters.db.models import CodeORM
from fanfan.core.models.code import CodeId
from fanfan.core.utils.code import get_qr_code_image


class CodeView(ModelView, model=CodeORM):
    name_plural = "Коды"
    icon = "fa-solid fa-qrcode"

    form_include_pk = True
    form_columns = [
        CodeORM.id,
        CodeORM.user,
        CodeORM.achievement,
        CodeORM.ticket,
    ]

    @action(
        name="show_qr_code",
        label="Вывести QR-код",
        add_in_list=False,
    )
    async def show_qr_code(self, request: Request) -> FileResponse:
        pk: str = request.query_params.get("pks", "").split(",")[0]
        return FileResponse(get_qr_code_image(CodeId(pk)), filename=f"code_{pk}.png")
