from functools import wraps
import logging
import sys
import time
from typing import Any, Callable, Optional

from flask import Flask
import psycopg2
from psycopg2.pool import SimpleConnectionPool


# Получение логгера с именем текущего модуля для записи логов
logger = logging.getLogger(__name__)


class ConnectionPool:
    """
    Реализация пула соединений с базой данных.

    Этот класс обеспечивает единичный экземпляр пула соединений, который
    управляет созданием и выдачей соединений к базе данных, используя
    минимальное и максимальное количество соединений.
    """

    _instance: Optional['ConnectionPool'] = None

    def __new__(
        cls, db_url: str, minconn: int = 1, maxconn: int = 20
    ) -> 'ConnectionPool':

        if cls._instance is None:
            # Создаем новый экземпляр, если он еще не создан
            cls._instance = super(ConnectionPool, cls).__new__(cls)
            cls._instance.connection_pool = SimpleConnectionPool(
                minconn, maxconn, db_url)

            logger.info(
                "Класс 'ConnectionPool', метод '__new__' ."
                "Инициализация пула соединений с db_url: %s, "
                "minconn: %d, maxconn: %d connection_pool: %s",
                db_url, minconn, maxconn, cls._instance.connection_pool
            )

        return cls._instance  # Возвращаем единственный экземпляр

    def get_connection(self):
        if self.connection_pool:
            connection = self.connection_pool.getconn()

            logger.info(
                "Класс 'ConnectionPool', метод 'get_connection'. "
                "Получено новое соединение из пула: %s",
                connection
            )

            return connection

    def release_connection(self, connection):

        if self.connection_pool:

            self.connection_pool.putconn(connection)

            logger.info(
                "Класс 'ConnectionPool', метод 'release_connection'. "
                "Соединение возвращено в пул: %s",
                connection
            )

    def close_connection_pool(self):

        if self.connection_pool:

            self.connection_pool.closeall()

            logger.debug(
                "Класс 'ConnectionPool', метод 'close_connection_pool'. "
                "Пул соединений закрыт. connection_pool: %s",
                self.connection_pool
            )


class DatabaseConnection:
    """Контекстный менеджер для работы с соединением к базе данных."""

    def __init__(self, connection_pool):
        self.connection_pool = connection_pool
        self.connection = None

    def __enter__(self):
        self.connection = self.connection_pool.get_connection()

        logger.debug(
            "Класс 'DatabaseConnection',  метод '__enter__'. "
            "Вход в контекстный менеджер, получено соединение: %s",
            self.connection
        )

        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connection:
            if exc_type is None:
                # Если нет исключений, коммитим изменения
                self.connection.commit()

                logger.debug(
                    "Класс 'DatabaseConnection',  метод '__exit__'. "
                    "Коммит изменений, соединение: %s",
                    self.connection
                )

            else:
                # Если было исключение, откатываем изменения
                self.connection.rollback()

                logger.error(
                    "Класс 'DatabaseConnection',  метод '__exit__'. "
                    "Откат изменений из-за исключения: '%s', %s",
                    exc_type, exc_val
                )

            self.connection_pool.release_connection(self.connection)

            logger.debug(
                "Класс 'DatabaseConnection',  метод '__exit__'. "
                "Выход из контекстного менеджера, соединение освобождено: %s",
                self.connection
            )


def db_connection(cursor_factory: Optional[Callable] = None):
    """ Декоратор для управления соединениями с базой данных.

    :param
        cursor_factory: Необязательный аргумент для создания курсора
        специфического типа.

    """

    def inner(func: Callable) -> Callable:

        @wraps(func)
        def wrapper(self, *args, **kwargs) -> Any:
            connection_pool = self.connection_pool  # Получаем пул соединений

            with DatabaseConnection(connection_pool) as conn:

                if cursor_factory is None:
                    with conn.cursor() as cursor:  # Стандартный курсор

                        logger.debug(
                            "Декоратор 'db_connection'. Функция '%s'. "
                            "Создан стандартный курсор.",
                            func.__name__
                        )

                        return func(self, cursor, *args, **kwargs)
                else:
                    with conn.cursor(cursor_factory=cursor_factory) as cursor:

                        logger.debug(
                            "Декоратор 'db_connection'. Функция '%s'. "
                            "Создан курсор с заданным factory: '%s'",
                            func.__name__, cursor_factory
                        )

                        return func(self, cursor, *args, **kwargs)

        return wrapper

    return inner


def retry_connection(limit: int = 5, interval: int = 5):
    """
    Декоратор для повторных попыток подключения к базе данных.

    param:
        limit: Максимальное количество попыток подключения.
        interval: Интервал между попытками в секундах.
    """
    def decorator(func):

        @wraps(func)
        def wrapper(*args, **kwargs):

            attempts = 0

            while attempts < limit:

                try:
                    logger.info(
                        "Декоратор 'retry_connection'. Функция '%s'. "
                        "Попытка подключения... попытка: %d",
                        func.__name__, attempts + 1
                    )

                    return func(*args, **kwargs)

                except psycopg2.Error as error:

                    attempts += 1

                    logger.error(
                        "Декоратор 'retry_connection'. Функция '%s'. "
                        "Ошибка при попытке подключения: '%s'. "
                        "Попытка %d из %d.",
                        func.__name__, error, attempts, limit, exc_info=True
                    )

                    if attempts < limit:
                        time.sleep(interval)

            logger.critical(
                "Декоратор 'retry_connection'. Функция '%s'. "
                "Все попытки подключения исчерпаны.",
                func.__name__, exc_info=True
            )

            raise psycopg2.Error("Все попытки подключения исчерпаны.")

        return wrapper

    return decorator


def create_signal_handler(app: Flask) -> callable:
    """
    Создает обработчик сигналов для корректного завершения работы приложения.
    """
    def signal_handler(sig, frame):
        """
        Создает обработчик сигналов для
        корректного завершения работы приложения.
        """
        logger.info(
            "Обработчик: 'create_signal_handler'. "
            "Получен сигнал: %d. Завершение работы приложения...",
            sig
        )

        app.connection_pool.close_connection_pool()  # Закрываем пул соединений

        logger.info(
            "Обработчик: 'create_signal_handler'. "
            "Пул соединений закрыт. Приложение завершено успешно."
        )

        sys.exit(0)  # Завершение работы с кодом 0 (без ошибок)

    return signal_handler
