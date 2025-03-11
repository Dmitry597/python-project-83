from datetime import datetime
from functools import wraps
import logging

import psycopg2
from psycopg2.extras import RealDictCursor

from page_analyzer.logging_config import setup_logging


logger = setup_logging(
    __name__,
    level=logging.WARNING,
    console_level=logging.INFO
)


def db_exception_handler(func):

    @wraps(func)
    def wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)
        except psycopg2.Error as error:
            logger.error(
                "Функция: '%s'. Ошибка 'БД'. Аргументы: [%r], ошибка: [%s]",
                func.__name__,
                (args, kwargs),
                error,

                exc_info=True
            )

        except Exception as error:

            logger.exception(
                "Функция: '%s'. Неожиданная ошибка при выполнении. "
                "Аргументы: [%r], ошибка: [%s]",
                func.__name__,
                (args, kwargs),
                error,

                exc_info=True
            )
    return wrapper


def add_log(func_name, id, result):

    if result:
        logger.info("Функция '%s', получены данные "
                    "для URL с 'id'=%s, данные: %s", func_name, id, result
                    )
    else:
        logger.warning("Функция '%s', данные не найдены "
                       "для URL с 'id'=%s", func_name, id)


class UrlRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    @db_exception_handler
    def get_connection(self):
        connection = psycopg2.connect(self.db_url)

        logger.info("Успешно установлено соединение с 'базой данных'.")

        return connection

    @db_exception_handler
    def find_url(self, id):

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM urls WHERE id = %s"
                cursor.execute(query, (id,))

                result = cursor.fetchone()

                add_log('find_url', id, result)

                return result

    @db_exception_handler
    def show_urls(self):

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT
                        urls.id,
                        urls.name,
                        url_checks.status_code,
                        url_checks.created_at,
                        urls.created_at AS url_created_at
                    FROM
                        urls
                    LEFT JOIN
                        url_checks ON urls.id = url_checks.url_id
                        AND url_checks.created_at = (
                            SELECT MAX(created_at)
                            FROM url_checks
                            WHERE urls.id = url_checks.url_id
                        )
                    ORDER BY
                        urls.created_at DESC;
                """
                cursor.execute(query)

                result = cursor.fetchall()

                if result:
                    logger.debug(
                        "Функция 'show_urls' получены данные %s", result
                    )
                else:
                    logger.warning(
                        "Функция 'show_urls', данные не найдены! "
                        "result = %s", result
                    )

                return result

    @db_exception_handler
    def save_url(self, url_data):

        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT id FROM urls WHERE name = %s LIMIT 1;"
                cursor.execute(query, (url_data,))
                url_id = cursor.fetchone()

                if url_id:
                    logger.info(
                        "Функция 'save_url', URL - %s уже существует, "
                        "id: %s!",
                        url_data, url_id[0]
                    )

                    return True, url_id[0]

                query = """
                    INSERT INTO urls (name, created_at)
                    VALUES (%s, %s)
                    RETURNING id
                """

                cursor.execute(query, (url_data, datetime.now()))

                url_id = cursor.fetchone()[0]

            conn.commit()

        logger.info(
            "Функция 'save_url', URL - %s успешно добавлен, "
            "получил id: %s!",
            url_data, url_id
        )

        return False, url_id

    @db_exception_handler
    def save_checks_url(self, url_id, status_code, h1, title, description):

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:

                try:
                    query = """
                        INSERT INTO url_checks (
                            url_id,
                            status_code,
                            h1,
                            title,
                            description,
                            created_at)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """

                    cursor.execute(query, (
                        url_id,
                        status_code,
                        h1,
                        title,
                        description,
                        datetime.now())
                    )

                    logger.info(
                        "Функция 'save_checks_url', успешно сохранила "
                        "данные: "
                        "'url_id': %s, "
                        "'status_code': %s, "
                        "'h1': %s, "
                        "'title': %s, "
                        "'description': %s, "
                        "'created_at': %s, ",

                        url_id,
                        status_code,
                        h1,
                        title,
                        description,
                        datetime.now()
                    )

                    return True

                except Exception as error:
                    logger.error(
                        "В функции 'save_checks_url' произошла ошибка "
                        "при добавление данных: %s, %s, %s, %s, %s, %s."
                        "Ошибка: [%s]",

                        url_id,
                        status_code,
                        h1,
                        title,
                        description,
                        datetime.now(),
                        str(error),

                        exc_info=True
                    )

                    return False

    @db_exception_handler
    def find_checks_urll(self, url_id):

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                        SELECT * FROM url_checks
                        WHERE url_id = %s
                        ORDER BY created_at DESC;
                    """
                cursor.execute(query, (url_id,))

                result = cursor.fetchall()

                add_log('find_checks_urll', url_id, result)

                return result
