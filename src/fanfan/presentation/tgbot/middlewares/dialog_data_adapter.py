from collections.abc import Awaitable, Callable
from typing import Any, Final, TypeVar

from adaptix import Retort, name_mapping
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from aiogram_dialog import DialogManager
from aiogram_dialog.manager.manager_middleware import MANAGER_KEY

DIALOG_DATA_ADAPTER_KEY: Final[str] = "dialog_data_adapter"
T = TypeVar("T")
_default_retort = Retort(
    recipe=[
        name_mapping(
            omit_default=True,
        ),
    ],
)


class DialogDataAdapter:
    def __init__(self, manager: DialogManager) -> None:
        self._manager = manager

    def load(
        self,
        model: type[T],
        /,
        *,
        retort: Retort = _default_retort,
    ) -> T:
        return retort.load(self._manager.dialog_data, model)

    def flush(
        self,
        model: Any,
        /,
        *,
        model_type: type | None = None,
        retort: Retort = _default_retort,
    ) -> None:
        self._manager.dialog_data.clear()
        self._manager.dialog_data.update(retort.dump(model, model_type or type(model)))


class DialogDataAdapterMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> None:
        if dialog_manager := data.get(MANAGER_KEY):
            data[DIALOG_DATA_ADAPTER_KEY] = DialogDataAdapter(dialog_manager)
        return await handler(event, data)
