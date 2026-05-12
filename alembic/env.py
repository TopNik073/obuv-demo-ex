import os
import re
import sys

from datetime import UTC
from datetime import datetime
from pathlib import Path

from alembic.script import ScriptDirectory

PROJECT_PATH: Path = Path(__file__).parent.parent

# Leading digits in custom revision ids (e.g. 0000_..., 0001_slug_...)
_REV_SEQ_DIGITS: int = 4

_bundle_src = PROJECT_PATH / 'src'
_path_insert: list[str] = []
if _bundle_src.is_dir():
    _path_insert.append(str(_bundle_src))
_path_insert.append(str(PROJECT_PATH))
sys.path = [*_path_insert, *sys.path]


def _env_file_dir() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return PROJECT_PATH


if os.getenv('POSTGRESQL_CONNECTION_STRING') is None:
    _env_path = _env_file_dir() / '.env'
    if _env_path.is_file():
        with _env_path.open(encoding='utf-8') as env_file:
            for line in env_file:
                split_line: list[str] = line[:-1].split('=', maxsplit=1)
                if len(split_line) == 2:
                    variable_name, variable_value = split_line
                    os.environ[variable_name] = variable_value



from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

import repository  # noqa: F401 — register ORM tables on metadata

from alembic import context
from core.config import config as app_config
from repository.base.models import BaseORM

config = context.config
fileConfig(config.config_file_name)

target_metadata = BaseORM.metadata


async def run_migrations_online():
    connectable = create_async_engine(
        app_config.POSTGRES_URL,
        poolclass=pool.NullPool,
        future=True,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def do_run_migrations(connection):
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        version_table_schema=target_metadata.schema,
        include_schemas=True,
        compare_type=True,
        compare_server_default=True,
        process_revision_directives=process_revision_directives,
    )

    with context.begin_transaction():
        context.run_migrations()


def _slugify_message(message: str | None) -> str:
    if not message or not message.strip():
        return ''
    s = message.strip().lower()
    s = re.sub(r'[\s/\\]+', '_', s)
    s = re.sub(r'[^\w]+', '_', s, flags=re.UNICODE)
    s = re.sub(r'_+', '_', s).strip('_')
    return s[:80]


def _next_rev_sequence(head_revision: str | None) -> int:
    if head_revision is None:
        return 0
    prefix = head_revision.split('_', 1)[0]
    if len(prefix) == _REV_SEQ_DIGITS and prefix.isdecimal():
        return int(prefix) + 1
    msg = (
        f'Alembic head {head_revision!r} must start with a 4-digit sequence '
        f'(e.g. 0000_...); adjust process_revision_directives or rename the head revision.'
    )
    raise ValueError(msg)


def process_revision_directives(
    context,
    revision,
    directives,
) -> None:
    if not directives:
        return

    migration_script = directives[0]
    head_revision = ScriptDirectory.from_config(context.config).get_current_head()
    seq = _next_rev_sequence(head_revision)
    ts = datetime.now(UTC).strftime('%Y_%m_%d_%H_%M_%S')
    slug = _slugify_message(migration_script.message)
    seq_part = f'{seq:0{_REV_SEQ_DIGITS}d}'
    if slug:
        migration_script.rev_id = f'{seq_part}_{ts}_{slug}'
    else:
        migration_script.rev_id = f'{seq_part}_{ts}'


if context.is_offline_mode():
    raise NotImplementedError('Offline mode is not supported for async migrations')
else:
    import asyncio

    asyncio.run(run_migrations_online())
