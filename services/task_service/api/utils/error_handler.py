import http

from aiohttp import web

import services.task_service.dto.base as dto
from services.task_service.api.exceptions import TaskServiceException

INTERNAL_ERROR_STATUS = dto.Status(error=True, message="Internal server error")


async def default_error_handler(
    request: web.Request,
    exc: Exception,
) -> web.Response:
    if isinstance(exc, TaskServiceException):
        return web.json_response(
            data={"status": exc.status.dict()},
            status=exc.status_code.value,
        )
    return web.json_response(
        {"status": INTERNAL_ERROR_STATUS.dict()},
        status=http.HTTPStatus.INTERNAL_SERVER_ERROR.value,
    )
