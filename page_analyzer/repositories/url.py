from datetime import datetime
import logging
from typing import Any, List, Optional, Dict, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor

from page_analyzer.db_connections.connection_manager import (
    ConnectionPool,
    db_connection,
    retry_connection
)


# Получение логгера с именем текущего модуля для записи логов
logger = logging.getLogger(__name__)


class UrlRepository:
    def __init__(self, connection_pool: 'ConnectionPool'):
        """
        Инициализирует UrlRepository с пулом соединений.

        :param
            connection_pool: Объект ConnectionPool,
            который управляет соединениями с базой данных.
        """
        self.connection_pool = connection_pool

    @retry_connection()
    @db_connection(cursor_factory=RealDictCursor)
    def find_url(self, cursor, id: int) -> Optional[Dict[str, Any]]:
        """
        Находит и возвращает данные URL из таблицы urls, по заданному
        идентификатору.
        """

        query = "SELECT * FROM urls WHERE id = %s"
        cursor.execute(query, (id,))

        result = cursor.fetchone()
        # добавляем логи
        UrlRepository.add_log('find_url', id, result)

        return result

    @retry_connection()
    @db_connection(cursor_factory=RealDictCursor)
    def show_urls(self, cursor) -> Optional[List[Dict[str, Any]]]:
        """
        Извлекает все URL-адреса из базы данных вместе
        с их статусами и метками времени последних проверок.
        """

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

    @retry_connection()
    @db_connection()
    def save_url(self, cursor, url_data: str) -> Tuple[bool, Any]:
        """
        Сохраняет URL в базе данных.

        Если URL уже существует, возвращает его идентификатор.
        Если URL новый, добавляет его в базу и возвращает его идентификатор.

        Returns:
            Кортеж, где первый элемент - булево значение,
                        указывающее, существует ли URL,
                        второй элемент - идентификатор URL.
        """

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

        logger.info(
            "Функция 'save_url', URL - %s успешно добавлен, "
            "получил id: %s!",
            url_data, url_id
        )
        # Возвращаем False, поскольку URL новый, и его идентификатор
        return False, url_id

    @retry_connection()
    @db_connection(cursor_factory=RealDictCursor)
    def save_checks_url(
        self, cursor,
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

        except psycopg2.Error as error:
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

    @retry_connection()
    @db_connection(cursor_factory=RealDictCursor)
    def find_checks_urll(self, cursor, url_id: int) -> List[Dict[str, Any]]:
        """
        Функция выполняет запрос к базе данных для получения всех
        записей о проверках URL, связанных с указанным идентификатором URL.

        Результаты сортируются по времени создания в порядке убывания.
        """

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
