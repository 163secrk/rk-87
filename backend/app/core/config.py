from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "金盾信贷风控审批系统"

    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = "Asd123.com"
    DB_NAME: str = "jindun_credit"

    SECRET_KEY: str = "jindun-credit-risk-management-secret-key-2024"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24

    BACKEND_CORS_ORIGINS: list = [
        "http://localhost:3087",
        "http://127.0.0.1:3087",
    ]

    class Config:
        case_sensitive = True
        env_file = ".env"


settings = Settings()
