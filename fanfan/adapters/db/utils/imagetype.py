from typing import Any

from fastapi_storages import StorageImage
from fastapi_storages.exceptions import ValidationException
from fastapi_storages.integrations.sqlalchemy import ImageType as _ImageType
from PIL import Image, UnidentifiedImageError
from sqlalchemy import Dialect

# https://github.com/aminalaee/sqladmin/issues/799#issuecomment-2333238928


class ImageType(_ImageType):
    def process_bind_param(self, value: Any, dialect: Dialect) -> str | None:  # noqa: ARG002
        if value is None:
            return value
        if len(value.file.read(1)) != 1:
            return None

        try:
            image_file = Image.open(value.file)
            image_file.verify()
        except UnidentifiedImageError:
            msg = "Invalid image file"
            raise ValidationException(msg)  # noqa: B904

        image = StorageImage(
            name=value.filename,
            storage=self.storage,
            height=image_file.height,
            width=image_file.width,
        )

        # Fix file corruption
        if value.size is None:
            return image.name

        image.write(file=value.file)

        image_file.close()
        value.file.close()
        return image.name
