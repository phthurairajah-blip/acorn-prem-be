from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    APP_NAME: str = "acorn-prem-be"
    ENV: str = "local"
    DATABASE_URL: str

    JWT_SECRET: str
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    RESET_TOKEN_EXPIRE_MINUTES: int = 30

    FRONTEND_URL: str = "http://localhost:3000"
    ADMIN_SEED_EMAIL: str = "admin@acorn.com"
    ADMIN_SEED_PASSWORD: str = "Acorn@123"
    ADMIN_SEED_ROLE: str = "ADMIN"

    BOOKING_ADMIN_EMAIL: str | None = None
    RECAPTCHA_SECRET: str | None = None

    MEDIA_DIR: str = "uploads"

    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_SERVER: str
    MAIL_PORT: int = 587
    MAIL_STARTTLS: bool = True
    MAIL_SSL_TLS: bool = False

settings = Settings()
