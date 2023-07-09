import io

import cv2
import numpy as np
from aiogram import Bot, F, Router
from aiogram.types import Message
from qreader import QReader

router = Router(name="qr_router")


@router.message(F.photo)
async def photo_msg(message: Message, bot: Bot):
    photo = await bot.get_file(file_id=message.photo[-1].file_id)
    binary = io.BytesIO()
    await bot.download_file(file_path=photo.file_path, destination=binary)
    qreader = QReader()
    image = cv2.cvtColor(
        cv2.imdecode(np.frombuffer(binary.read(), np.uint8), 1), cv2.COLOR_BGR2RGB
    )
    decoded_text = qreader.decode(image=image)
    if decoded_text:
        await message.reply(text=f"Вижу QR-код! Содержимое: {decoded_text}")
    else:
        await message.reply(text=f"Красивое фото, но QR-кода я на нём не вижу 😔")
