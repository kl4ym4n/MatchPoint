import typing

from aiohttp.web_request import FileField
from pydantic import ConfigDict

from dto.base import BaseDTO
from dto.base import TaskStatus
from sqlalchemy.dialects.postgresql import JSONB

__all__ = [
    "TaskDTO",
]


class TaskDTO(BaseDTO):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: typing.Optional[int] = None
    filename: typing.Optional[str] = None
    file: FileField
    status: TaskStatus = TaskStatus.QUEUED
    description: typing.Optional[str] = None
    is_deleted: bool = False
    url: typing.Optional[str] = None
    result: typing.Optional[JSONB] = None
