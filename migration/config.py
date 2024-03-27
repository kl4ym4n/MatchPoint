import typing
from pathlib import Path

from pydantic_settings import BaseSettings

BASE_PATH = Path(__file__).parent


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
    POSTGRES_CONFIG: PostgresConfig = PostgresConfig()


SETTINGS = Settings()
