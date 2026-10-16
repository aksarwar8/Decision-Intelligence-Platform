import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    APP_NAME = os.getenv("APP_NAME", "Decision Intelligence Platform")
    APP_VERSION = os.getenv("APP_VERSION", "0.1.0")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")

    DATABASE_URL = os.getenv("DATABASE_URL")

    M5_DATA_DIRECTORY = os.getenv("M5_DATA_DIRECTORY", "data/raw/m5")
    REPLAY_DATE = os.getenv("REPLAY_DATE", "2022-01-01")


settings = Settings()