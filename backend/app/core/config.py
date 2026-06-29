from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "OpenPNCP API"
    DATABASE_URL: str = "sqlite:///./openpncp.db"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
