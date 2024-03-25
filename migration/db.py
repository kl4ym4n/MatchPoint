import enum

import sqlalchemy_utils as sau
import typer

from services.config import POSTGRES_CONFIG

CONNECTION_STRING = POSTGRES_CONFIG.sync_connection_string


class TaskType(str, enum.Enum):
    CREATE = "create"
    DROP = "drop"
    RECREATE = "recreate"


def main(task: TaskType = TaskType.CREATE):
    if task is TaskType.CREATE:
        sau.create_database(CONNECTION_STRING)
    elif task is TaskType.DROP:
        sau.drop_database(CONNECTION_STRING)
    elif task is TaskType.RECREATE:
        sau.drop_database(CONNECTION_STRING)
        sau.create_database(CONNECTION_STRING)
    else:
        raise ValueError(f"Unexpected task type {task}")


if __name__ == "__main__":
    typer.run(main)
