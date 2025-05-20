from typing import Any
from pydantic import model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    SECRET_KEY: str
    ALGORITHM: str
    DATABASE_URL: str | None = None
    
    @model_validator(mode='after')
    def get_database_url(self) -> Any:
        self.DATABASE_URL = f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
        return self
    
    class ConfigDict:
        env_file = ".env"
        
settings = Settings()