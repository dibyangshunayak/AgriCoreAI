import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the project (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str = ""
    WEATHER_API_KEY: str = ""
    NVIDIA_API_KEY: str = ""
    NVIDIA_MODEL: str = "nvidia/nemotron-3-nano-30b-a3b"
    NVIDIA_API_URL: str = "https://integrate.api.nvidia.com/v1/chat/completions"
    NVIDIA_TIMEOUT: float = 4.0

    # Database
    DATABASE_URL: str = "sqlite:///../data/agricore.db"

    # JWT Settings
    JWT_SECRET: str = "agricore-access-secret-987654321"
    JWT_REFRESH_SECRET: str = "agricore-refresh-secret-123456789"
    JWT_ACCESS_EXPIRATION_MINUTES: int = 15
    JWT_REFRESH_EXPIRATION_DAYS: int = 7

    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str = "agricore-mock-google-client-id.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET: str = "agricore-mock-google-client-secret"


    # API Server Config
    HOST: str = "127.0.0.1"
    PORT: int = 8000
    SECRET_KEY: str = "agricore-super-secret-key-12345"

    # Pydantic Settings configuration to load .env
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
