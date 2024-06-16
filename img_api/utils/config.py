from dotenv import load_dotenv
import os

from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file='.env.img_api')

    DEBUG: str = os.getenv('DEBUG')
    TITLE: str = os.getenv('TITLE')
    VERSION: str = '1.0.0'
    DESCRIPTION: str = os.getenv('DESCRIPTION')
    OPENAPI_PREFIX: str = os.getenv('OPENAPI_PREFIX')
    DOCS_URL: str = '/docs'
    REDOC_URL: str = '/redoc'
    OPENAPI_URL: str = '/openapi.json'
    API_PREFIX: str = '/api'
    DB_ECHO_LOG: bool = True if os.getenv('DEBUG') == 'True' else False

    POSTGRES_USER: str = os.getenv('POSTGRES_USER')
    POSTGRES_PASSWORD: str = os.getenv('POSTGRES_PASSWORD')
    POSTGRES_DB: str = os.getenv('POSTGRES_DB')
    POSTGRES_SERVER: str = os.getenv('POSTGRES_SERVER')
    POSTGRES_PORT: str = os.getenv('POSTGRES_PORT')
    POSTGRES_TEST_SERVER: str = os.getenv('POSTGRES_TEST_SERVER')
    POSTGRES_TEST_DB: str = os.getenv('POSTGRES_TEST_DB')
    POSTGRES_TEST_PORT: str = os.getenv('POSTGRES_TEST_PORT')
    DB_ECHO_LOG: bool = True if os.getenv('DEBUG') == 'True' else False

    GW_ROOT_URL: str = os.getenv('GW_ROOT_URL')
    AUTH_USER: str = os.getenv('AUTH_USER')
    AUTH_PASSWORD: str = os.getenv('AUTH_PASSWORD')

    LOGGING_CONFIG: dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "standard": {"format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"},
        },
        "handlers": {
            "default": {
                "level": "INFO",
                "formatter": "standard",
                "class": "logging.StreamHandler",
                "stream": "ext://sys.stdout",
            },
        },
        "loggers": {
            "": {
                "level": "INFO",
                "handlers": ["default"],
                "propagate": False,
            },
            "uvicorn.error": {
                "level": "DEBUG",
                "handlers": ["default"],
            },
            "uvicorn.access": {
                "level": "DEBUG",
                "handlers": ["default"],
            },
        },
    }

    @property
    def sync_database_url(self) -> str:
        return (
            f'postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )

    @property
    def async_database_url(self) -> str:
        return (
            f'postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}'
            f'@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}'
        )


settings = Settings()
