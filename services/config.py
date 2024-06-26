import typing
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_PATH = Path(__file__).parent


# Minio config
class MinioConfig(BaseSettings):
    MINIO_HOST: str = "s3"
    MINIO_PORT: str = "9000"
    MINIO_USER: str = "root"
    MINIO_PASSWORD: str = "password"
    MINIO_BUCKET: str = "taskfiles"
    MINIO_ACCESS_KEY: str = "5JVspZSmZhWNvAErGe86"
    MINIO_SECRET_KEY: str = "tWyIWjwfDMwNEaoQqqrcVU21IWwTGF4HQUvGtdsn"


# Rabbit config
class RabbitConfig(BaseSettings):
    RABBIT_HOST: str = "rabbitmq"
    RABBIT_PORT: int = 5672
    RABBIT_USER: str = "guest"
    RABBIT_PASSWORD: str = "guest"

    @property
    def connection_string(self) -> str:
        return (
            f"amqp://{self.RABBIT_USER}:{self.RABBIT_PASSWORD}@{self.RABBIT_HOST}:{self.RABBIT_PORT}/"
        )


# Postgres config
class PostgresConfig(BaseSettings):
    DB_HOST: str = "db"
    DB_PORT: int = 5432
    DB_NAME: str = "app"
    DB_USER: str = "user"
    DB_PASSWORD: str = "password"

    def get_connection_string(
        self,
        driver: typing.Optional[str] = None,
        database: typing.Optional[str] = None,
    ) -> str:
        if database is None:
            database = self.DB_NAME
        if driver is None:
            driver = ""
        else:
            driver = f"+{driver}"
        return f"postgresql{driver}://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{database}"

    @property
    def connection_string(self) -> str:
        return self.get_connection_string("asyncpg")

    @property
    def sync_connection_string(self) -> str:
        return self.get_connection_string()


class Settings(BaseSettings):
    QUEUE_NAME: str = "task_queue"
    EXCHANGE_NAME: str = 'task_exchange'
    RABBIT_CONFIG: RabbitConfig = RabbitConfig()
    POSTGRES_CONFIG: PostgresConfig = PostgresConfig()
    MINIO_CONFIG: MinioConfig = MinioConfig()


SETTINGS = Settings()
