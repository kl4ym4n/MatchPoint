from pathlib import Path

from alembic import command
from alembic.config import Config

from config import SETTINGS


def run_migrations(dsn: str) -> None:
    root_path = Path(__file__).absolute().parent.parent
    alembic_cfg_path = root_path / "alembic.ini"
    script_location = root_path / "migration"

    alembic_cfg = Config(alembic_cfg_path)
    alembic_cfg.set_main_option("script_location", script_location.as_posix())
    alembic_cfg.set_main_option("sqlalchemy.url", dsn)
    command.upgrade(alembic_cfg, "head")


if __name__ == "__main__":
    run_migrations(SETTINGS.POSTGRES_CONFIG.sync_connection_string)
