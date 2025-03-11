import logging
from urllib.parse import urlparse

import validators
from flask import abort, current_app

from page_analyzer.models.url_repository import UrlRepository
from page_analyzer.services.parser import PageAnalyzer
from page_analyzer.logging_config import setup_logging


logger = setup_logging(
    __name__,
    level=logging.WARNING,
    console_level=logging.INFO
)


def get_url_repository():
    return UrlRepository(current_app.config['DATABASE_URL'])


def handle_new_url(url, url_repo):

    logger.debug("Функция: 'handle_new_url'. Полученный URL: %s", url)

    normalize_url = '://'.join(urlparse(url)[:2])

    logger.debug(
        "Функция: 'handle_new_url'. Нормализованный URL: %s",
        normalize_url
    )
    try:
        info, id_url = url_repo.save_url(normalize_url)

        logger.debug(
            "Функция: 'handle_new_url'. Сохранила результат: "
            "'info'=%s, 'id_url'=%s}",
            info, id_url
        )

        if info:
            message, category = 'Страница уже существует', 'info'
        else:
            message, category = 'Страница успешно добавлена', 'success'

        logger.debug(
            "Функция: 'handle_new_url'."
            "Полученное сообщение: '%s', категория: '%s'",
            message, category
        )

        return message, category, id_url

    except Exception as e:
        logging.error(
            "Функция: 'handle_new_url'.Неизвестная ошибка: %s",
            e,
            exc_info=True
        )

        return 'Неизвестная ошибка', 'danger', None


def handle_checks_url(url_id, url_repo):
    logger.debug("Функция: 'handle_checks_url'. Полученный URL_ID: %s", url_id)

    info_url = url_repo.find_url(url_id)

    if not info_url:
        logger.error(
            "Функция: 'handle_checks_url'. Не найден URL для ID: %s", url_id
        )
        return 'Не удалось найти URL', 'danger'

    logger.debug(
        "Функция: 'handle_checks_url'. Найденная информация о URL: %s",
        info_url
    )

    analyzer = PageAnalyzer(info_url['name'])

    errors = analyzer.get_page_content()

    if errors:
        message, category = errors['message'], errors['category']

        logger.warning(
            "Функция: 'handle_checks_url'. Ошибка при анализе страницы: %s",
            errors
        )
    else:
        logger.debug(
            "Функция: 'handle_checks_url'. Полученный статус кода: '%s'",
            analyzer.status_code
        )

        status_save_url = url_repo.save_checks_url(
            url_id,
            analyzer.status_code,
            analyzer.h1,
            analyzer.title,
            analyzer.description
        )

        if status_save_url:
            logger.info(
                "Функция: 'handle_checks_url'. "
                "Страница успешно проверена для ID: %s",
                url_id
            )
            message, category = 'Страница успешно проверена', 'success'
        else:
            logger.error(
                "Функция: 'handle_checks_url'. "
                "Ошибка при сохранении проверки для ID: %s", url_id
            )
            abort(500)

    return message, category


def validate(url):
    logger.debug("Начало валидации URL: '%s'", url)

    errors = {}

    if not validators.url(url):
        errors['message'] = 'Некорректный URL'

    if len(url) > 255:
        errors['message'] = 'URL превышает 255 символов'

    if errors:
        logger.debug(
            "Функция: 'validate'. Ошибки валидации для URL '%s': %s",
            url, errors
        )
    else:
        logger.info(
            "Функция: 'validate'. Валидация URL прошла успешно: '%s'",
            url
        )

    return errors
