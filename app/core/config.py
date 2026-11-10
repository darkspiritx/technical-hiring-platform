
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    DB_HOST: str
    DB_PORT: int = 5432
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    # Resend Email API
    RESEND_API_KEY: str = ""
    EMAIL_FROM: str = ""

    # Backend URL for verification links
    BACKEND_URL: str = "http://127.0.0.1:8000"

    FRONTEND_URL: str = "http://localhost:5174"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()
