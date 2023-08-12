from aiogram import F, Router, types

router = Router(name="callbacks_router")


@router.callback_query(F.data == "delete")
async def delete_message(callback: types.CallbackQuery):
    await callback.message.delete()
