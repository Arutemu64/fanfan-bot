from sqladmin import ModelView, action
from starlette.requests import Request
from starlette.responses import FileResponse

from fanfan.common import QR_CODES_TEMP_DIR
from fanfan.core.models.qr import QR, QRType
from fanfan.core.utils.qr import generate_img
from fanfan.infrastructure.db.models import Achievement


class AchievementView(ModelView, model=Achievement):
    name_plural = "Достижения"
    icon = "fa-solid fa-trophy"
    column_default_sort = [(Achievement.order, False)]

    column_list = [Achievement.order, Achievement.title, Achievement.description]
    column_details_exclude_list = [Achievement.user_received]
    form_columns = [
        Achievement.order,
        Achievement.title,
        Achievement.description,
        Achievement.secret_id,
    ]

    column_labels = {
        Achievement.id: "ID",
        Achievement.order: "Порядок",
        Achievement.secret_id: "Секретный ID",
        Achievement.title: "Название",
        Achievement.description: "Описание",
        Achievement.created_on: "Время создания",
        Achievement.updated_on: "Время изменения",
    }

    @action(
        name="show_qr_code",
        label="Вывести QR-код",
        add_in_list=False,
    )
    async def show_qr_code(self, request: Request) -> FileResponse:
        pk = request.query_params.get("pks", "").split(",")[0]
        achievement = await self.get_object_for_details(pk)
        qr = QR(type=QRType.ACHIEVEMENT, data=str(achievement.secret_id))
        qr_file_path = QR_CODES_TEMP_DIR.joinpath(f"{hash(qr)}.png")
        if not qr_file_path.is_file():
            generate_img(qr).save(qr_file_path)
        return FileResponse(qr_file_path)
