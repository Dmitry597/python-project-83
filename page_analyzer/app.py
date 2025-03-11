from flask import Flask
from dotenv import load_dotenv

from page_analyzer.config import Config
from page_analyzer.views.url_views import error_handlers, url_blueprint


load_dotenv()


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

    app.register_blueprint(url_blueprint)  # Регистрирует blueprint

    error_handlers(app)  # Устанавливает обработчики ошибок для приложения

    return app  # Возвращает настроенное приложение


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
