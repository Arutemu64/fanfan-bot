import pytz
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import DialogManager, Window
from aiogram_dialog.widgets.input import ManagedTextInput, TextInput
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo
from aiogram_dialog.widgets.text import Const, Jinja
from croniter import croniter
from dishka import AsyncContainer

from fanfan.adapters.config_reader import Configuration
from fanfan.application.common.task_manager import TaskManager
from fanfan.core.exceptions.base import AppException
from fanfan.presentation.tgbot import states
from fanfan.presentation.tgbot.dialogs.common.widgets import Title
from fanfan.presentation.tgbot.ui import strings

DATA_SELECTED_TASK_NAME = "selected_task_name"


async def tasks_menu_getter(
    dialog_manager: DialogManager,
    container: AsyncContainer,
    **kwargs,
) -> dict:
    task_manager: TaskManager = await container.get(TaskManager)
    update_tickets_status = await task_manager.get_update_tickets_status()
    config: Configuration = await container.get(Configuration)

    update_tickets_last_execution = update_tickets_status.last_execution.astimezone(
        tz=pytz.timezone(config.timezone)
    ).strftime("%H:%M %d.%m.%Y")

    return {
        "update_tickets_running": update_tickets_status.running,
        "update_tickets_last_execution": update_tickets_last_execution,
        "update_tickets_cron": update_tickets_status.cron,
    }


async def update_tickets_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    container: AsyncContainer = manager.middleware_data["container"]
    task_manager: TaskManager = await container.get(TaskManager)

    try:
        await task_manager.update_tickets()
    except AppException as e:
        await callback.answer(e.message, show_alert=True)
        return
    else:
        await callback.answer("✅ Задача поставлена в очередь!")


async def update_cron_handler(
    message: Message,
    widget: ManagedTextInput,
    dialog_manager: DialogManager,
    data: str,
) -> None:
    task_name: str = dialog_manager.dialog_data[DATA_SELECTED_TASK_NAME]
    container: AsyncContainer = dialog_manager.middleware_data["container"]
    task_manager: TaskManager = await container.get(TaskManager)
    if croniter.is_valid(data):
        await task_manager.set_task_cron(task_name, data)
    else:
        await task_manager.set_task_cron(task_name, None)
    await dialog_manager.switch_to(states.Org.tasks)


async def switch_to_cron_input_handler(
    callback: CallbackQuery,
    button: Button,
    manager: DialogManager,
) -> None:
    manager.dialog_data[DATA_SELECTED_TASK_NAME] = button.widget_id
    await manager.switch_to(states.Org.input_task_cron)


input_cron_window = Window(
    Const(
        "⌨️ Задайте корректное cron выражение для задачи"
        " (или некорректное для отключения cron)"
    ),
    TextInput(id="cron_input", type_factory=str, on_success=update_cron_handler),
    SwitchTo(Const(strings.buttons.back), state=states.Org.tasks, id="back"),
    state=states.Org.input_task_cron,
)


tasks_window = Window(
    Title(Const(strings.titles.tasks)),
    Const("<b>🎫 Обновление билетов</b>"),
    Jinja(
        "<b>Состояние:</b> {% if update_tickets_running %}▶️ Выполняется"
        "{% else %}⏹️ Не выполняется{% endif %}"
    ),
    Jinja("<b>Последнее успешное выполнение:</b> {{update_tickets_last_execution}}"),
    Row(
        Button(
            Const("🎫 Загрузить билеты"),
            id="run_update_tickets",
            on_click=update_tickets_handler,
        ),
        Button(
            Jinja(
                "cron: {% if update_tickets_cron %}{{ update_tickets_cron }}"
                "{% else %}Задать cron{% endif %}"
            ),
            id="update_tickets",
            on_click=switch_to_cron_input_handler,
        ),
    ),
    Button(
        Const(strings.buttons.update),
        id="refresh",
    ),
    SwitchTo(Const(strings.buttons.back), state=states.Org.main, id="back"),
    getter=tasks_menu_getter,
    state=states.Org.tasks,
)
