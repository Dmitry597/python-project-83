from datetime import datetime
import logging
from typing import Any, List, Optional, Dict, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor

from page_analyzer.repositories.database_exceptions import db_exception_handler


# Получение логгера с именем текущего модуля для записи логов
logger = logging.getLogger(__name__)


class UrlRepository:
    def __init__(self, db_url: str):
        """
        Инициализация репозитория URL.

        Params:
            db_url: URL для подключения к базе данных.
        """
        self.db_url = db_url

    @db_exception_handler
    def get_connection(self) -> psycopg2.extensions.connection:
        """
        Получение соединения с базой данных.

        Returns:
            Any: Объект соединения с базой данных.

        """

        connection = psycopg2.connect(self.db_url)

        logger.info("Успешно установлено соединение с 'базой данных'.")

        return connection

    @db_exception_handler
    def find_url(self, id: int) -> Optional[Dict[str, Any]]:
        """
        Находит и возвращает данные URL из таблицы urls, по заданному
        идентификатору.
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM urls WHERE id = %s"
                cursor.execute(query, (id,))

                result = cursor.fetchone()
                # добавляем логи
                UrlRepository.add_log('find_url', id, result)

                return result

    @db_exception_handler
    def show_urls(self) -> Optional[List[Dict[str, Any]]]:
        """
        Извлекает все URL-адреса из базы данных вместе
        с их статусами и метками времени последних проверок.
        """

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
    def save_url(self, url_data: str) -> Tuple[bool, Any]:
        """
        Сохраняет URL в базе данных.

        Если URL уже существует, возвращает его идентификатор.
        Если URL новый, добавляет его в базу и возвращает его идентификатор.

        Returns:
            Кортеж, где первый элемент - булево значение,
                        указывающее, существует ли URL,
                        второй элемент - идентификатор URL.
        """

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
                    # noqa Возвращаем True, поскольку URL существует, и его идентификатор
                    return True, url_id[0]

                query = """
                    INSERT INTO urls (name, created_at)
                    VALUES (%s, %s)
                    RETURNING id
                """

                cursor.execute(query, (url_data, datetime.now()))

                url_id = cursor.fetchone()[0] # noqa Получаем идентификатор нового URL

            conn.commit()

        logger.info(
            "Функция 'save_url', URL - %s успешно добавлен, "
            "получил id: %s!",
            url_data, url_id
        )
        # Возвращаем False, поскольку URL новый, и его идентификатор
        return False, url_id

    @db_exception_handler
    def save_checks_url(
        self,
        url_id: int, status_code: int, h1: str, title: str, description: str
    ) -> bool:
        """
        Сохраняет данные проверки URL-адреса в базу данных 'url_checks'.

        Params:
            url_id: Уникальный идентификатор проверяемого URL-адреса.
            status_code: Код состояния HTTP, возвращаемый во время проверки.
            h1: тег H1 содержимого URL-адреса.
            title: название содержимого URL-адреса.
            description: Краткое описание содержимого URL-адреса.

        Returns:
            Возвращает True, если вставка прошла успешно,
            и False, если произошла ошибка.

        """

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
    def find_checks_urll(self, url_id: int) -> List[Dict[str, Any]]:
        """
        Функция выполняет запрос к базе данных для получения всех
        записей о проверках URL, связанных с указанным идентификатором URL.

        Результаты сортируются по времени создания в порядке убывания.
        """

        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                        SELECT * FROM url_checks
                        WHERE url_id = %s
                        ORDER BY created_at DESC;
                    """
                cursor.execute(query, (url_id,))

                result = cursor.fetchall()

                UrlRepository.add_log('find_checks_urll', url_id, result)

                return result

    @staticmethod
    def add_log(func_name: str, id: int, result: dict) -> None:
        """
        Записывает информацию в лог о выполнении функции
        и результатах её операции.
        """

        if result:
            logger.info(
                "Функция '%s', получены данные "
                "для URL с 'id'=%s, данные: %s",
                func_name, id, result
            )
        else:
            logger.info(
                "Функция '%s', данные не найдены "
                "для URL с 'id'=%s",
                func_name, id
            )
