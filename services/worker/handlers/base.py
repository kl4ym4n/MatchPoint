import abc
import typing as t
from services import dto
from services.dao.factory import DaoFactory
from services.task_service.api.utils.annotations import DictStrAny
from services.worker.exceptions import HandlerException


class BaseHandler(abc.ABC):
    def __init__(
            self,
            database_url: str,
    ) -> None:
        self.factory = DaoFactory(database_url=database_url)


class BaseTaskHandler(BaseHandler, abc.ABC):
    async def get_task(self, task_id: int) -> dto.TaskDTO:
        async with self.factory.session_maker() as session:
            task_dao = await self.factory.create_task_dao(session)
            task: t.Optional[dto.TaskDTO] = await task_dao.get_by_id(task_id)
            if task is None:
                raise HandlerException("Task not found")
            return task

    async def update_task(self, data: DictStrAny) -> None:
        async with self.factory.session_maker.begin() as session:
            task_dao = await self.factory.create_task_dao(session)
            task = await self.get_task(data["task_id"])
            task.status = data['status']
            if data.get('result'):
                task.result = data['result']
            await task_dao.update(task.id, task)

