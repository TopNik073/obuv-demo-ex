from pathlib import Path

from pydantic import AliasChoices
from pydantic import Field
from pydantic import SecretStr
from pydantic_settings import BaseSettings
from pydantic_settings import SettingsConfigDict

from core.paths import config_root


class Config(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(config_root() / '.env'),
        env_file_encoding='utf-8',
        extra='ignore',
    )

    SENSITIVE_DATA: list[str] = [
        'username',
        'password',
    ]

    APP_NAME: str = 'Обувь'
    APP_VERSION: str = '0.1.0'
    APP_HOST: str = '127.0.0.1'
    APP_PORT: int = 8000
    DEBUG: bool = False

    SQLITE_DATABASE_PATH: Path = Path('obuv.sqlite')
    SQLALCHEMY_DATABASE_URI: str | None = Field(
        default=None,
        validation_alias=AliasChoices('DATABASE_URL', 'SQLALCHEMY_DATABASE_URI'),
    )

    SQLALCHEMY_ECHO: bool = False

    JWT_SECRET: SecretStr
    JWT_ALGORITHM: str = 'HS256'
    JWT_ACCESS_EXPIRE_MINUTES: int = 30
    JWT_REFRESH_EXPIRE_MINUTES: int = 43200

    ADMIN_BOOTSTRAP_USERNAME: str = 'admin'
    ADMIN_BOOTSTRAP_PASSWORD: SecretStr | None = None

    LOG_LEVEL: str = 'INFO'
    LOG_TO_FILE: bool = False
    LOGS_DIR: Path = Path('logs')
    LOG_DATE_FORMAT: str = '%Y-%m-%dT%H:%M:%S'

    @property
    def sqlite_database_file(self) -> Path:
        p = self.SQLITE_DATABASE_PATH
        if p.is_absolute():
            return p
        return config_root() / p

    @property
    def DATABASE_URL(self) -> str:
        if self.SQLALCHEMY_DATABASE_URI:
            return self.SQLALCHEMY_DATABASE_URI
        path = self.sqlite_database_file.resolve()
        return f'sqlite+aiosqlite:///{path.as_posix()}'


config = Config()
