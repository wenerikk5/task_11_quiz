import os
from dotenv import load_dotenv
from abc import ABC

load_dotenv()


class Config(ABC):
    APP_TITLE = "Quiz"
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "1234")
    DATABASE_URL = f'postgresql+asyncpg://{POSTGRES_USER}:' + \
        f'{POSTGRES_PASSWORD}@db:{POSTGRES_PORT}/postgres'
    SQL_COMMAND_ECHO = False


class DevelopmentConfig(Config):
    DATABASE_URL = 'sqlite+aiosqlite:///./db.sqlite'


class ProductionConfig(Config):
    ...


def get_config() -> Config:
    env = os.getenv("ENV")
    if env == "development":
        return DevelopmentConfig()
    return ProductionConfig()


config = get_config()
