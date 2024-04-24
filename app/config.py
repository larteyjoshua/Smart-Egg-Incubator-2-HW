import os
from functools import lru_cache
import secrets
from pydantic_settings import BaseSettings
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())


class Settings(BaseSettings):
    SECRET_KEY: str = secrets.token_urlsafe(32)
    SERVER_URL: str = os.environ.get("SERVER_URL")
    DEVICE_ID_ENCRYPTION_KEY: str = os.environ.get("DEVICE_ID_ENCRYPTION_KEY")
    
    class Config:
        case_sensitive = True
        env_file = ".env"
        extra = "allow"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
