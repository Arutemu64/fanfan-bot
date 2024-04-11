from sqladmin import ModelView, action
from starlette.requests import Request
from starlette.responses import FileResponse

from fanfan.application.dto.qr import QR
from fanfan.common.enums import QRType
from fanfan.infrastructure.db.models import Achievement
from fanfan.presentation.tgbot.dialogs.menus.main.qr_pass import QR_CODES_TEMP_DIR


class AchievementView(ModelView, model=Achievement):
    name_plural = "Достижения"
    icon = "fa-solid fa-trophy"
    column_labels = {
        Achievement.id: "ID",
        Achievement.title: "Название",
        Achievement.description: "Описание",
        Achievement.created_on: "Время создания",
        Achievement.updated_on: "Время изменения",
    }
    column_list = [Achievement.title, Achievement.description]
    column_details_exclude_list = [Achievement.user_received]
    form_columns = [Achievement.title, Achievement.description]

    @action(
        name="show_qr_code",
        label="Вывести QR-код",
        add_in_list=False,
    )
    async def show_qr_code(self, request: Request):
        pk = request.query_params.get("pks", "").split(",")[0]
        achievement = await self.get_object_for_details(pk)
        qr = QR(type=QRType.ACHIEVEMENT, data=str(achievement.secret_id))
        qr_file_path = QR_CODES_TEMP_DIR.joinpath(f"{hash(qr)}.png")
        if not qr_file_path.is_file():
            qr.generate_img().save(qr_file_path)
        return FileResponse(qr_file_path)
