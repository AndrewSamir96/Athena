from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    llm_api_key: str
    cors_origins: list[str] = ["*"]

    class Config:
        env_file = ".env"


settings = Settings()
