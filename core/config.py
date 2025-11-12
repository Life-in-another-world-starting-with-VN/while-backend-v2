from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "mysql+pymysql://root:hugerich77@localhost:3306/gstar_db"
    JWT_SECRET_KEY: str = "your-secret-key-here-change-in-production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Gemini API Settings
    GEMINI_TOKEN: str = ""
    GEMINI_MODEL: str = "gemini-2.0-flash"

    # FAL API Settings
    FAL_KEY: str = ""
    FAL_URL: str = ""
    
    # Google AI Image Generation Settings
    IMAGE_MODEL: str = "gemini-2.5-flash-image"
    IMAGE_SIZE: str = "16:9"

    model_config = SettingsConfigDict(env_file=".env")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
