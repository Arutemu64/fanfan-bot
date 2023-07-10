from pathlib import Path

from aiocache import Cache
from aiogram.types import FSInputFile

cache = Cache()


async def set_media_id(path: Path, media_id: str) -> None:
    await cache.set(key=path.absolute(), value=media_id)
    return


async def get_media(path: Path) -> str | FSInputFile:
    if await cache.exists(key=path.absolute()):
        return await cache.get(key=path.absolute())
    else:
        return FSInputFile(path=path)
