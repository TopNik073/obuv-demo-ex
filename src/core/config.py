from pathlib import Path

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    model_config = SettingsConfigDict(env_file='../.env', env_file_encoding='utf-8')

    SENSITIVE_DATA: list[str] = [
        'username',
        'password',
    ]

    APP_NAME: str = 'Обувь'
    APP_VERSION: str = '0.1.0'
    APP_HOST: str = '127.0.0.1'
    APP_PORT: int = 8000
    DEBUG: bool = False

    DB_HOST: str
    DB_PORT: str
    DB_USER: str
    DB_PASS: SecretStr
    DB_NAME: str

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
    def POSTGRES_URL(self) -> str:
        return f'postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS.get_secret_value()}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}'


config = Config()
