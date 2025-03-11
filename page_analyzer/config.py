import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    """
    Класс конфигурации для приложения.

    Класс содержит настройки, необходимые для работы приложения.

    """

    SECRET_KEY: str = os.getenv('SECRET_KEY')
    DATABASE_URL: str = os.getenv('DATABASE_URL')
