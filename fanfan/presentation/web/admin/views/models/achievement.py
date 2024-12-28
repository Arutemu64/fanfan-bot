from sqladmin import ModelView, action
from starlette.requests import Request
from starlette.responses import FileResponse

from fanfan.adapters.db.models import DBAchievement
from fanfan.common.paths import QR_CODES_TEMP_DIR
from fanfan.core.dto.qr import QR, QRType
from fanfan.core.utils.qr import generate_img


class AchievementView(ModelView, model=DBAchievement):
    name_plural = "Достижения"
    category = "Квест"
    icon = "fa-solid fa-trophy"
    column_default_sort = [(DBAchievement.order, False)]

    column_list = [DBAchievement.order, DBAchievement.title, DBAchievement.description]
    column_details_exclude_list = [DBAchievement.user_received]
    form_columns = [
        DBAchievement.order,
        DBAchievement.title,
        DBAchievement.description,
        DBAchievement.secret_id,
    ]

    column_labels = {
        DBAchievement.id: "ID",
        DBAchievement.order: "Порядок",
        DBAchievement.secret_id: "Секретный ID",
        DBAchievement.title: "Название",
        DBAchievement.description: "Описание",
        DBAchievement.created_at: "Время создания",
        DBAchievement.updated_at: "Время изменения",
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
        qr_file_path = QR_CODES_TEMP_DIR.joinpath(f"achievement_{achievement.id}.png")
        if not qr_file_path.is_file():
            generate_img(qr).save(qr_file_path)
        return FileResponse(qr_file_path)
