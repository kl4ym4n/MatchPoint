import sqlalchemy as sa
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import JSONB

from services.dto.base import TaskStatus

Base = declarative_base()


class Task(Base):
    __tablename__ = 'tasks'

    id = sa.Column(sa.Integer, primary_key=True)
    filename = sa.Column(sa.String)
    description = sa.Column(sa.String)
    status = sa.Column(sa.Enum(TaskStatus), nullable=False, default=TaskStatus.QUEUED)
    is_deleted = sa.Column(sa.Boolean)
    url = sa.Column(sa.String)
    result = sa.Column(JSONB)
