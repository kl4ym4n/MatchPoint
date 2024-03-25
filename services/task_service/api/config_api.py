from pathlib import Path

from pydantic_settings import BaseSettings

BASE_PATH = Path(__file__).parent


class Settings(BaseSettings):
    URL_PREFIX: str = "/api"

    # Server configs
    SERVER_HOST: str = "0.0.0.0"
    SERVER_PORT: int = 8080
    MAX_TASK_CHUNK_SIZE: int = 1000


API_SETTINGS = Settings()
