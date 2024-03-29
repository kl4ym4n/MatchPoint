import sqlalchemy.ext.asyncio as sa_async

from services import dto
from services.dao.base import BaseDAO
from services.dao.models import Task

__all__ = ["DaoFactory", "SqlAlchemyEngine"]


class SqlAlchemyEngine:
    def __init__(self, database_url: str):
        self.engine = sa_async.create_async_engine(database_url)
        self.session_maker = sa_async.async_sessionmaker(
            self.engine, expire_on_commit=False
        )

    async def close(self):
        await self.engine.dispose()


class DaoFactory:
    def __init__(self, database_url: str):
        self._engine = SqlAlchemyEngine(database_url)

    @property
    def session_maker(self):
        return self._engine.session_maker

    @staticmethod
    async def create_task_dao(session: sa_async.AsyncSession) -> BaseDAO:
        return BaseDAO(Task, dto.TaskDTO, session)

    async def close(self):
        await self._engine.close()
