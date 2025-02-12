from pydantic_settings import BaseSettings
from dotenv import load_dotenv
# Explicitly load .env file
load_dotenv()

class Settings(BaseSettings):
    DATABASE_URL: str
    FLUTTERWAVE_SECRET_KEY: str
    FLUTTERWAVE_PUBLIC_KEY: str
    FLW_ENCRYPTION_KEY: str

    class Config:
        env_file = ".env"

settings = Settings()