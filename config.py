from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    user_db: str
    database_db: str
    host_db: str
    password_db: str
    port_db: int
    redis_url: str

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings():
    return Settings()