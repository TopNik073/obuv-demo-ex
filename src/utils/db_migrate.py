from alembic.config import Config

from alembic import command
from core.paths import bundle_root


def run_migrations() -> None:
    ini = bundle_root() / 'alembic.ini'
    if not ini.is_file():
        msg = f'alembic.ini missing at {ini}'
        raise RuntimeError(msg)
    cfg = Config(str(ini))
    command.upgrade(cfg, 'head')
