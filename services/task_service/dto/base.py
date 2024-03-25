import enum
import typing

from pydantic import BaseModel


class TaskStatus(enum.Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    ERROR = "error"

    def is_done(self):
        return self not in [self.QUEUED, self.RUNNING]

    def is_error(self):
        return self == self.ERROR


class BaseDTO(BaseModel):
    def dict(self, by_alias=True, **kwargs):
        return super().model_dump(
            by_alias=by_alias,
            **kwargs,
        )

    def json(self, by_alias=True, **kwargs):
        return super().model_dump_json(
            by_alias=by_alias,
            **kwargs,
        )


class Pagination(BaseDTO):
    page: int = 1
    page_size: int = 10
    count: typing.Optional[int] = None

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size


class Status(BaseDTO):
    error: bool
    message: str
    extended: typing.Optional[typing.List[str]] = None
