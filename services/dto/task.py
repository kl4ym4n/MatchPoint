import typing

from aiohttp.web_request import FileField
from pydantic import ConfigDict

from services.dto.base import BaseDTO
from services.dto.base import TaskStatus

__all__ = [
    "TaskDTO",
]


class TaskDTO(BaseDTO):
    model_config = ConfigDict(from_attributes=True, arbitrary_types_allowed=True)

    id: typing.Optional[int] = None
    filename: typing.Optional[str] = None
    file: typing.Optional[FileField] = None
    status: TaskStatus = TaskStatus.QUEUED
    description: typing.Optional[str] = None
    is_deleted: bool = False
    url: typing.Optional[str] = None
    result: typing.Optional[str] = None
