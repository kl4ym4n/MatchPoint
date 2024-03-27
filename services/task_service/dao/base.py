import typing
from typing import Generic
from typing import Type
from typing import TypeVar

import sqlalchemy as sa
import sqlalchemy.ext.asyncio as sa_async

import dto
from dao.models import Base

__all__ = [
    "BaseDAO",
]

MODEL_TYPE = TypeVar("MODEL_TYPE", bound=Base)
DATA_TYPE = TypeVar("DATA_TYPE", bound=dto.BaseDTO)


class BaseDAO(Generic[MODEL_TYPE, DATA_TYPE]):
    def __init__(
            self,
            model_class: Type[MODEL_TYPE],
            dto_class: Type[DATA_TYPE],
            session: sa_async.AsyncSession,
    ):
        self.model_class = model_class
        self.dto_class = dto_class
        self.session = session

    async def get_by_id(self, _id: int) -> typing.Optional[DATA_TYPE]:
        stmt = sa.select(self.model_class).filter(self.model_class.id == _id)
        result = await self.session.execute(stmt)
        model_instance = result.scalar_one_or_none()
        if model_instance is None:
            return None
        return self.dto_class.model_validate(model_instance)

    async def create(self, dto_obj: DATA_TYPE) -> DATA_TYPE:
        model_instance = self.model_class(**dto_obj.dict())
        self.session.add(model_instance)
        await self.session.flush()
        await self.session.refresh(model_instance)
        return self.dto_class.model_validate(model_instance)

    async def update(self, _id: int, dto_obj: DATA_TYPE) -> typing.Optional[DATA_TYPE]:
        result = await self.session.execute(
            sa.select(self.model_class).filter(self.model_class.id == _id)
        )
        model_instance = result.scalar_one_or_none()
        if model_instance is None:
            return None
        for key, value in dto_obj.dict().items():
            setattr(model_instance, key, value)
        await self.session.flush()
        return self.dto_class.model_validate(model_instance)

    async def delete(self, _id: int) -> None:
        result = await self.session.execute(
            sa.select(self.model_class).filter(self.model_class.id == _id)
        )
        model_instance = result.scalar_one_or_none()
        if model_instance:
            await self.session.delete(model_instance)
            await self.session.commit()

    async def get_all(
            self,
            filters: typing.Optional[typing.Dict[str, typing.Any]] = None,
            pagination: typing.Optional[dto.Pagination] = None,
            order_desc: bool = True,
    ) -> typing.List[DATA_TYPE]:
        if filters is None:
            filters = {}

        query = sa.select(self.model_class)
        for attr, value in filters.items():
            if hasattr(self.model_class, attr):
                query = query.filter(getattr(self.model_class, attr) == value)
        query = query.filter(False == getattr(self.model_class, 'is_deleted'))
        if pagination:
            pagination.count = (
                await self.session.execute(
                    sa.select(sa.func.count()).select_from(
                        query
                    )
                )
            ).scalar_one()
            query = query.offset(pagination.offset).limit(pagination.page_size)
        if order_desc:
            query = query.order_by(self.model_class.id.desc())
        results = await self.session.execute(query)
        models = results.scalars().all()
        return [self.dto_class.model_validate(model) for model in models]
