import io

import pydantic
from aiohttp import web
import os

import dto
from api.exceptions import BadRequestException
from api.exceptions import NotFoundException
from api.views.base import BaseListView
from api.views.base import BaseView
from dao.factory import DaoFactory
from minio import Minio

from config import SETTINGS

__all__ = [
    "TaskHandler",
    "TaskListHandler",
]

minio_client = Minio(SETTINGS.MINIO_CONFIG.MINIO_HOST + ":" + SETTINGS.MINIO_CONFIG.MINIO_PORT,
                     access_key=SETTINGS.MINIO_CONFIG.MINIO_ACCESS_KEY,
                     secret_key=SETTINGS.MINIO_CONFIG.MINIO_SECRET_KEY,
                     secure=False)


class TaskHandler(BaseView):
    async def get(self) -> web.Response:
        task_id = int(self.request.match_info.get("task_id"))

        factory: DaoFactory = self.request.app["factory"]
        async with factory.session_maker() as session:
            task_dao = await factory.create_task_dao(session)
            task = await task_dao.get_by_id(task_id)
            if task is None:
                raise NotFoundException(f"Task with id {task_id} does not exist")

        return web.json_response({"Task": task.dict(mode="json")})

    async def put(self) -> web.Response:
        task_id = int(self.request.match_info.get("task_id"))
        try:
            task_data = dto.TaskDTO(**await self._get_data())
        except pydantic.ValidationError as e:
            raise BadRequestException(str(e)) from e

        factory: DaoFactory = self.request.app["factory"]
        async with factory.session_maker() as session:
            task_dao = await factory.create_task_dao(session)
            task = await task_dao.update(task_id, task_data)
            if task is None:
                raise NotFoundException(f"Task with id {task_id} does not exist")
            await session.commit()
        return web.json_response({"Task": task.dict(mode="json")})

    async def delete(self) -> web.Response:
        task_id = int(self.request.match_info.get("task_id"))

        factory: DaoFactory = self.request.app["factory"]
        async with factory.session_maker() as session:
            task_dao = await factory.create_task_dao(session)
            await task_dao.delete(task_id)
            await session.commit()
        return web.json_response({})


class TaskListHandler(BaseListView):
    async def get(self) -> web.Response:
        pagination = dto.Pagination(**dict(self.request.query))

        factory: DaoFactory = self.request.app["factory"]
        async with factory.session_maker() as session:
            task_dao = await factory.create_task_dao(session)
            tasks = await task_dao.get_all(pagination=pagination)

        return web.json_response(
            {
                "tasks": [t.dict(mode="json") for t in tasks],
                "meta": pagination.dict(),
            }
        )

    async def post(self) -> web.Response:
        try:
            task_data = dto.TaskDTO(**await self._get_form_data())
        except pydantic.ValidationError as e:
            raise BadRequestException(str(e)) from e

        print(task_data)

        file = task_data.file
        file_content = file.file
        file_content.seek(0, os.SEEK_END)
        file_length = file_content.tell()
        file_content.seek(0)

        minio_client.put_object(SETTINGS.MINIO_CONFIG.MINIO_BUCKET, file.filename, file_content, file_length)

        factory: DaoFactory = self.request.app["factory"]
        async with factory.session_maker() as session:
            task_dao = await factory.create_task_dao(session)
            del task_data.file
            task = await task_dao.create(task_data)

            await session.commit()

        return web.json_response({"Task": task.dict(mode="json")})
