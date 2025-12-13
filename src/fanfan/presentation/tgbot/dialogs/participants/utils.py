import datetime
import json
from dataclasses import dataclass

from fanfan.core.models.participant import ParticipantValue
from fanfan.core.vo.participant import ParticipantId, ValueType


@dataclass(frozen=True, slots=True)
class ImageValue:
    filename: str


@dataclass(frozen=True, slots=True, kw_only=True)
class FileValue:
    # Hosted on Cosplay2
    filename: str | None = None
    filesize: int | None = None
    fileext: str | None = None

    # Link
    link: str | None = None


def build_cosplay2_file_link(event_id: int, request_id: int, filename: str) -> str:
    return f"https://cosplay2.ru/uploads/{event_id}/{request_id}/{filename}"


def build_cosplay2_image_link(event_id: int, request_id: int, filename: str) -> str:
    return f"https://cosplay2.ru/uploads/{event_id}/{request_id}/{filename}.jpg"


def parse_checkbox_value(value: ParticipantValue) -> bool:
    return value.value == "YES"


def parse_image_value(value: ParticipantValue) -> ImageValue:
    image_info = json.loads(value.value)
    filename = image_info["filename"]
    return ImageValue(filename)


def parse_file_value(value: ParticipantValue) -> FileValue:
    file_info = json.loads(value.value)
    if file_info.get("filename"):
        return FileValue(
            filename=file_info["filename"],
            filesize=file_info["filesize"],
            fileext=file_info["fileext"],
        )
    return FileValue(
        link=file_info["link"],
    )


def parse_duration_value(value: ParticipantValue) -> datetime.timedelta:
    return datetime.timedelta(minutes=float(value.value))


def parse_value(
    value: ParticipantValue, participant_id: ParticipantId, event_id: int
) -> str | None:
    if value.value is None:
        return None
    if value.type is ValueType.CHECKBOX:
        return "Да" if parse_checkbox_value(value) else "Нет"
    if value.type is ValueType.IMAGE:
        image_value = parse_image_value(value)
        return build_cosplay2_image_link(
            event_id=event_id,
            request_id=participant_id,
            filename=image_value.filename,
        )
    if value.type is ValueType.FILE:
        file_value = parse_file_value(value)
        if file_value.filename:
            return build_cosplay2_file_link(
                event_id=event_id,
                request_id=participant_id,
                filename=file_value.filename,
            )
        return file_value.link
    if value.type is ValueType.DURATION:
        td = parse_duration_value(value)
        total_seconds = int(td.total_seconds())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
    return str(value.value)
