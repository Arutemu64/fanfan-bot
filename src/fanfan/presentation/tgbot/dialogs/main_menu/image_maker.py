import io

from aiogram import Bot
from aiogram.enums import ContentType
from aiogram.types import BufferedInputFile, Message
from aiogram_dialog import DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const
from dishka import FromDishka
from dishka.integrations.aiogram_dialog import inject
from PIL import Image

from fanfan.core.dto.notification import DEFAULT_REPLY_MARKUP
from fanfan.presentation.tgbot import UI_IMAGES_DIR, states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.static import strings

OVERLAY_IMAGE_PATH = UI_IMAGES_DIR / "overlay.png"


def make_image(base_image_buffer: io.BytesIO) -> io.BytesIO:
    base_img = Image.open(base_image_buffer)
    overlay_img = Image.open(OVERLAY_IMAGE_PATH)

    target_size = overlay_img.width
    width, height = base_img.size
    square_side = min(width, height)

    left = (width - square_side) // 2
    top = (height - square_side) // 2
    right = left + square_side
    bottom = top + square_side

    cropped_img = base_img.crop((left, top, right, bottom))
    resized_base = cropped_img.resize(
        (target_size, target_size), Image.Resampling.LANCZOS
    )

    if resized_base.mode != "RGBA":
        resized_base = resized_base.convert("RGBA")

    final_img = Image.alpha_composite(
        resized_base,
        overlay_img.resize((target_size, target_size), Image.Resampling.LANCZOS),
    )

    output_buffer = io.BytesIO()
    final_img.save(output_buffer, format="PNG")
    output_buffer.seek(0)

    return output_buffer


@inject
async def image_maker_handler(
    message: Message,
    message_input: MessageInput,
    manager: DialogManager,
    bot: FromDishka[Bot],
):
    await bot.send_chat_action(chat_id=message.chat.id, action="upload_photo")
    file_id = message.photo[-1].file_id
    base_image_buffer = await bot.download(file_id)
    final_image_buffer = make_image(base_image_buffer)
    await message.answer_photo(
        photo=BufferedInputFile(final_image_buffer.read(), filename="final_image.png"),
        caption="✨ А вот и фото! Скорее публикуй эту красоту в своих социальных "
        "сетях.\nИ не забудь про хештеги #УвидимсяНаFANFAN #fanfan2026 😙",
        reply_markup=DEFAULT_REPLY_MARKUP,
    )
    manager.show_mode = ShowMode.NO_UPDATE


image_maker_window = Window(
    Title(Const(strings.titles.image_maker)),
    StaticMedia(path=UI_IMAGES_DIR.joinpath("overlay_demo.png")),
    Const(
        "Хочешь красивое фото для анонса в своих соцсетях? 📸\n"
        "Пришли своё фото, а мы сделаем всё остальное!\n\n"
        "<i>Постарайся прислать фото формата 1:1 или уместиться в центре. "
        "В этом тебе поможет встроенный редактор Telegram.</i>"
    ),
    MessageInput(image_maker_handler, content_types=[ContentType.PHOTO]),
    SwitchTo(
        Const(strings.buttons.back),
        id="back",
        state=states.Main.HOME,
    ),
    state=states.Main.IMAGE_MAKER,
)
