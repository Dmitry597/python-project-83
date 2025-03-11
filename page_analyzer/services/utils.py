import logging
from urllib.parse import urlparse

import validators
from flask import abort, current_app

from page_analyzer.models.url_repository import UrlRepository
from page_analyzer.services.parser import PageAnalyzer
from page_analyzer.logging_config import setup_logging


# Настраиваем логирование для текущего модуля
logger = setup_logging(
    __name__,  # Имя логгера будет соответствовать имени текущего модуля
    level=logging.WARNING,  # Устанавливаем уровень логирования для файла
    console_level=logging.INFO  # Устанавливаем уровень логирования для консоли
)


def get_url_repository() -> UrlRepository:
    """
    Создает экземпляр UrlRepository с использованием URL базы данных
    из конфигурации текущего приложения.
    """
    return UrlRepository(current_app.config['DATABASE_URL'])


def handle_new_url(
    url: str, url_repo: UrlRepository
) -> tuple[str, str, int | None]:

    """
    Обрабатывает новый URL, нормализует его и сохраняет в репозитории.

    Returns:
            Сообщение о результате операции, категория (успех или ошибка),
            ID сохраненного URL или None в случае ошибки.
    """

    logger.debug("Функция: 'handle_new_url'. Полученный URL: %s", url)
    # Нормализуем URL
    normalize_url = '://'.join(urlparse(url)[:2])

    logger.debug(
        "Функция: 'handle_new_url'. Нормализованный URL: %s",
        normalize_url
    )
    try:
        # Сохраняем нормализованный URL в репозитории
        info, id_url = url_repo.save_url(normalize_url)

        logger.debug(
            "Функция: 'handle_new_url'. Сохранила результат: "
            "'info'=%s, 'id_url'=%s}",
            info, id_url
        )
        # Формируем сообщение и категорию в зависимости от результата сохранения
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


def handle_checks_url(
    url_id: int, url_repo: 'UrlRepository'
) -> tuple[str, str]:
    """
    Обрабатывает проверку URL, извлекая информацию о странице и
    сохраняя результаты проверки.

    Params:
        url_id: Уникальный идентификатор URL для проверки.
        url_repo: Экземпляр класса репозитория URL,
        который используется для работы с данными URL.

    Returns:
        Сообщение о результате проверки и его категорию.
    """

    logger.debug("Функция: 'handle_checks_url'. Полученный URL_ID: %s", url_id)
    # Извлекаем информацию о URL по его идентификатору
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
    # Создаем объект анализатора страницы с использованием извлеченного URL
    analyzer = PageAnalyzer(info_url['name'])
    # Получаем содержимое страницы и проверяем наличие ошибок
    errors = analyzer.get_page_content()

    if errors:
        # Если ошибок нет, сохраняем результаты проверки URL
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
            # Если данные успешно сохранены, возвращаем сообщение об успехе
            message, category = 'Страница успешно проверена', 'success'
        else:
            logger.error(
                "Функция: 'handle_checks_url'. "
                "Ошибка при сохранении проверки для ID: %s", url_id
            )
            # Если возникла ошибка при сохранении, вызываем ошибку сервера
            abort(500)

    return message, category


def validate(url: str) -> dict:
    """
    Проверяет корректность указанного URL.

    Возвращает cловарь с сообщениями об ошибках, если таковые имеются.
    Если ошибок нет, возвращается пустой словарь.
    """
    logger.debug("Начало валидации URL: '%s'", url)

    errors = {}

    if not validators.url(url):  # Проверка на корректность формата URL
        errors['message'] = 'Некорректный URL'

    if len(url) > 255:   # Проверка длины URL
        errors['message'] = 'URL превышает 255 символов'

    # Если есть ошибки, логируем их, иначе логируем успешную валидацию
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
