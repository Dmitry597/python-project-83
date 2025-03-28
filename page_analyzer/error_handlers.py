import logging

from flask import Flask, render_template


# Получение логгера с именем текущего модуля для записи логов
logger = logging.getLogger(__name__)


def handle_error(app: Flask) -> callable:
    """
    Регистрация обработчиков ошибок для приложения Flask.

    Обработчики ошибок позволяют управлять ситуациями, когда возникают
    ошибки, такие как 404 (страница не найдена) и общие исключения.

    param:
          Экземпляр приложения Flask, для которого регистрируются обработчики.
    """

    @app.errorhandler(404)
    def page_not_found(error: Exception):
        """
        Обработчик для ошибок 404 (страница не найдена).

        При возникновении ошибки 404, этот обработчик
        отобразит специальную страницу для пользователей.

        Param:
                Информация об ошибке 404.
        Return:
                Страницу для отображения ошибки 404 и статус код 404.
        """

        logger.error(
            "Обработчик: 'page_not_found'. "
            "Ошибка 404. Информация об ошибке: %s",
            error,
            exc_info=True
        )

        return render_template('page404.html'), 404

    @app.errorhandler(Exception)
    def handle_general_exception(error: Exception):
        """
        Обработчик для всех остальных исключений.

        Когда происходит ошибка, обработчик регистрирует информацию о
        возникшей ошибке, включая код ошибки и ее детали, и возвращает
        HTML-страницу, отображающую сообщение об ошибке.

        """

        error_code = getattr(error, 'code', 500)

        logger.critical(
            "Обработчик ошибок: 'handle_general_exception'. "
            "Ошибка сервера с кодом: %s "
            "Информация об ошибке: %s",
            error_code,
            error,
            exc_info=True
        )

        return render_template(
            'page500.html',
            error_code=error_code
        ), error_code
