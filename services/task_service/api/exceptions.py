import typing
from http import HTTPStatus

import dto.base as dto
from dto.base import Status


class TaskServiceException(Exception):
    def __init__(self, status: Status, status_code: HTTPStatus):
        super().__init__(status.message)
        self.status = status
        self.status_code = status_code


class BadRequestException(TaskServiceException):
    def __init__(
        self,
        message: str,
        extended: typing.Optional[typing.List[str]] = None,
    ):
        super().__init__(
            dto.Status(error=True, message=message, extended=extended),
            HTTPStatus.BAD_REQUEST,
        )


class NotFoundException(TaskServiceException):
    def __init__(
        self,
        message: str,
        extended: typing.Optional[typing.List[str]] = None,
    ):
        super().__init__(
            dto.Status(error=True, message=message, extended=extended),
            HTTPStatus.NOT_FOUND,
        )


class WrongBodyFormatException(TaskServiceException):
    def __init__(
        self,
        message: str,
        extended: typing.Optional[typing.List[str]] = None,
    ):
        super().__init__(
            dto.Status(error=True, message=message, extended=extended),
            HTTPStatus.BAD_REQUEST,
        )
