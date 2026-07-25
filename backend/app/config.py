from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://marketing_user:marketing_pass@localhost:5432/marketing_db"
    REDIS_URL: str = "redis://localhost:6379"
    SECRET_KEY: str = ""  # MUST be set via .env or environment variable
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"

    # OpenAI
    OPENAI_API_KEY: str = ""

    # Social APIs
    INSTAGRAM_APP_ID: str = ""
    INSTAGRAM_APP_SECRET: str = ""
    TIKTOK_APP_ID: str = ""
    TIKTOK_APP_SECRET: str = ""
    TWITTER_API_KEY: str = ""
    TWITTER_API_SECRET: str = ""
    TWITTER_BEARER_TOKEN: str = ""

    class Config:
        env_file = ".env"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
