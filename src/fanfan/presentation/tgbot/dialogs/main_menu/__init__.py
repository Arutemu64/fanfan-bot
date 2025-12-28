from aiogram import Router
from aiogram_dialog import Dialog, LaunchMode

from .home import main_window
from .image_maker import image_maker_window

main_menu_router = Router(name="main_menu_router")

main_menu_dialog = Dialog(
    main_window,
    image_maker_window,
    launch_mode=LaunchMode.ROOT,
)

main_menu_router.include_routers(main_menu_dialog)
