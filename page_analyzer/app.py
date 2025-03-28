import signal

from flask import Flask
from dotenv import load_dotenv

from page_analyzer.config import Config
from page_analyzer.db_connections.connection_manager import (
    ConnectionPool, create_signal_handler
)
from page_analyzer.error_handlers import handle_error
from page_analyzer.log_setup import setup_logging
from page_analyzer.repositories.url import UrlRepository
from page_analyzer.views.url_views import url_blueprint


load_dotenv()  # Загрузка файл .env, для настройки переменных окружения из него

setup_logging()  # Инициализация логирования


def create_app() -> Flask:
    """
    Создает и настраивает экземпляр приложения Flask.

    Функция 'create_app' инициализирует приложение, загружает конфигурацию из
    объекта Config, регистрирует маршруты и устанавливает обработчики ошибок.

    Returns:
        Flask: Настроенное экземпляр Flask-приложения.
    """

    app = Flask(__name__)

    app.config.from_object(Config)  # Загружает конфигурацию из класса Config

    database_url = app.config.get("DATABASE_URL")
    app.connection_pool = ConnectionPool(database_url)  # noqa Инициализация пула соединений

    app.url_repo = UrlRepository(app.connection_pool)  # noqa Инициализация UrlsRepository

    app.register_blueprint(url_blueprint)  # Регистрирует blueprint

    handle_error(app)  # Устанавливает обработчики ошибок для приложения

    # Установка обработчиков сигналов
    handler = create_signal_handler(app)
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    return app  # Возвращает настроенное приложение


if __name__ == "__main__":
    app = create_app()
    app.run(debug=False)
