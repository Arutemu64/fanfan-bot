import pytz
from aiogram.types import CallbackQuery
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.kbd import Button, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import AsyncContainer

from fanfan.adapters.config_reader import Configuration
from fanfan.application.common.task_manager import TaskManager
from fanfan.core.exceptions.base import AppException
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings


async def tasks_menu_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    task_manager: TaskManager = await container.get(TaskManager)
    import_tickets_status = await task_manager.get_import_tickets_status()
    import_from_c2_status = await task_manager.get_import_from_c2_status()
    config: Configuration = await container.get(Configuration)

    if import_tickets_status.last_execution:
        import_tickets_last_execution = import_tickets_status.last_execution.astimezone(
            tz=pytz.timezone(config.timezone)
        ).strftime("%H:%M %d.%m.%Y")
    else:
        import_tickets_last_execution = None

    if import_from_c2_status.last_execution:
        import_from_c2_status_last_execution = (
            import_from_c2_status.last_execution.astimezone(
                tz=pytz.timezone(config.timezone)
            ).strftime("%H:%M %d.%m.%Y")
        )
    else:
        import_from_c2_status_last_execution = None

    return {
        # Import tickets
        "import_tickets_running": import_tickets_status.running,
        "import_tickets_last_execution": import_tickets_last_execution,
        # Import from C2
        "import_from_c2_running": import_from_c2_status.running,
        "import_from_c2_last_execution": import_from_c2_status_last_execution,
    }


async def import_tickets_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    task_manager: TaskManager = await container.get(TaskManager)

    try:
        await task_manager.import_tickets()
    except AppException as e:
        await callback.answer(e.message, show_alert=True)
        return
    else:
        await callback.answer("✅ Задача поставлена в очередь")


async def import_from_c2_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    task_manager: TaskManager = await container.get(TaskManager)

    try:
        await task_manager.import_from_c2()
    except AppException as e:
        await callback.answer(e.message, show_alert=True)
        return
    else:
        await callback.answer("✅ Задача поставлена в очередь")


tasks_window = Window(
    Title(Const(strings.titles.tasks)),
    Const("<b>🎫 Импорт билетов</b>"),
    Jinja(
        "<b>Состояние:</b> {% if import_tickets_running %}▶️ Выполняется"
        "{% else %}⏹️ Не выполняется{% endif %}"
    ),
    Jinja("<b>Последнее успешное выполнение:</b> {{import_tickets_last_execution}}"),
    Const(" "),
    Const("<b>👯‍♀️ Импорт с Cosplay2</b>"),
    Jinja(
        "<b>Состояние:</b> {% if import_from_c2_running %}▶️ Выполняется"
        "{% else %}⏹️ Не выполняется{% endif %}"
    ),
    Jinja("<b>Последнее успешное выполнение:</b> {{import_from_c2_last_execution}}"),
    Button(
        Const("🎫 Импорт билетов"),
        id="run_import_tickets",
        on_click=import_tickets_handler,
    ),
    Button(
        Const("👯‍♀️ Импорт с Cosplay2"),
        id="run_import_from_c2",
        on_click=import_from_c2_handler,
    ),
    Button(
        Const(strings.buttons.update),
        id="refresh",
    ),
    SwitchTo(Const(strings.buttons.back), state=states.Org.main, id="back"),
    getter=tasks_menu_getter,
    state=states.Org.tasks,
)
