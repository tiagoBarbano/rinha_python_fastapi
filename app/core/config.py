from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    user_db: str
    database_db: str
    host_db: str
    password_db: str
    port_db: int
    database_url: str
    num_con_pg: int

    model_config = SettingsConfigDict(env_file=".env")

@lru_cache()
def get_settings():
    return Settings()