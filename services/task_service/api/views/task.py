import json

import pydantic
from aiohttp import web
import os

from services import dto
import pika
from api.exceptions import BadRequestException
from api.exceptions import NotFoundException
from api.views.base import BaseListView
from api.views.base import BaseView
from services.dao.factory import DaoFactory
from minio import Minio

from services import config

__all__ = [
    "TaskHandler",
    "TaskListHandler",
]

minio_client = Minio(config.SETTINGS.MINIO_CONFIG.MINIO_HOST + ":" + config.SETTINGS.MINIO_CONFIG.MINIO_PORT,
                     access_key=config.SETTINGS.MINIO_CONFIG.MINIO_ACCESS_KEY,
                     secret_key=config.SETTINGS.MINIO_CONFIG.MINIO_SECRET_KEY,
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
            task_data = dto.TaskDTO(**{"is_deleted": "true", "id": task_id})
            task = await task_dao.update(task_id, task_data)
            if task is None:
                raise NotFoundException(f"Task with id {task_id} does not exist")
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
                "tasks": [t.list_dict(mode="json") for t in tasks],
                "meta": pagination.dict(),
            }
        )

    async def post(self) -> web.Response:
        try:
            task_data = dto.TaskDTO(**await self._get_form_data())
        except pydantic.ValidationError as e:
            raise BadRequestException(str(e)) from e

        file = task_data.file

        if file is None:
            raise BadRequestException(f"File required")

        file_content = file.file
        file_content.seek(0, os.SEEK_END)
        file_length = file_content.tell()
        file_content.seek(0)

        minio_client.put_object(config.SETTINGS.MINIO_CONFIG.MINIO_BUCKET, file.filename, file_content, file_length)

        url = minio_client.get_presigned_url(
            "GET",
            config.SETTINGS.MINIO_CONFIG.MINIO_BUCKET,
            file.filename
        )

        factory: DaoFactory = self.request.app["factory"]
        async with factory.session_maker() as session:
            task_dao = await factory.create_task_dao(session)
            task_data.filename = file.filename
            task_data.url = url
            del task_data.file
            task = await task_dao.create(task_data)

            connection = pika.BlockingConnection(pika.ConnectionParameters(config.SETTINGS.RABBIT_CONFIG.RABBIT_HOST))
            channel = connection.channel()

            channel.queue_declare(queue=config.SETTINGS.QUEUE_NAME)

            message = {"id": task.id, "object": file.filename, "url": task.url}

            channel.basic_publish(exchange='', routing_key=config.SETTINGS.QUEUE_NAME, body=json.dumps(message))

            connection.close()

            await session.commit()

        return web.json_response({"Task": task.dict(mode="json")})
