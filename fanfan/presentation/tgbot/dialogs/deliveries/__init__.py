from aiogram_dialog import Dialog

from .windows import (
    create_delivery_window,
    delete_delivery_window,
    main_delivery_window,
)

dialog = Dialog(
    main_delivery_window,
    create_delivery_window,
    delete_delivery_window,
)
