import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

# Base directory of the project (backend/)
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    WEATHER_API_KEY: str = os.getenv("WEATHER_API_KEY", "")
    NVIDIA_API_KEY: str = os.getenv("NVIDIA_API_KEY", "")
    NVIDIA_MODEL: str = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-nano-30b-a3b")
    NVIDIA_API_URL: str = os.getenv("NVIDIA_API_URL", "https://integrate.api.nvidia.com/v1/chat/completions")
    NVIDIA_TIMEOUT: float = float(os.getenv("NVIDIA_TIMEOUT", 15.0))

    # Database
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite:///../data/agricore.db"
    )

    # JWT Settings
    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "agricore-access-secret-987654321"
    )
    JWT_REFRESH_SECRET: str = os.getenv(
        "JWT_REFRESH_SECRET",
        "agricore-refresh-secret-123456789"
    )
    JWT_ACCESS_EXPIRATION_MINUTES: int = int(os.getenv("JWT_ACCESS_EXPIRATION_MINUTES", 15))
    JWT_REFRESH_EXPIRATION_DAYS: int = int(os.getenv("JWT_REFRESH_EXPIRATION_DAYS", 7))

    # Google OAuth Settings
    GOOGLE_CLIENT_ID: str = os.getenv(
        "GOOGLE_CLIENT_ID",
        "agricore-mock-google-client-id.apps.googleusercontent.com"
    )
    GOOGLE_CLIENT_SECRET: str = os.getenv(
        "GOOGLE_CLIENT_SECRET",
        "agricore-mock-google-client-secret"
    )

    # API Server Config
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", 8000))
    SECRET_KEY: str = os.getenv(
        "SECRET_KEY",
        "agricore-super-secret-key-12345"
    )
    ALLOWED_ORIGINS: str = os.getenv("ALLOWED_ORIGINS", "")

    # Pydantic Settings configuration to load .env
    model_config = SettingsConfigDict(
        env_file=os.path.join(BASE_DIR, ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

settings = Settings()
