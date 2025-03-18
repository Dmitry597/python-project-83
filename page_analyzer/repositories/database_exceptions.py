from functools import wraps
import logging
from typing import Callable, Any, Optional

import psycopg2


# Получение логгера с именем текущего модуля для записи логов
logger = logging.getLogger(__name__)


def db_exception_handler(
    func: Callable[..., Any]
) -> Callable[..., Optional[Any]]:

    """
    Декоратор для обработки исключений базы данных.

    Этот декоратор обрабатывает исключения, возникающие в функции,
    и записывает информацию об ошибках в лог.

    Если возникает ошибка `psycopg2.Error`, она логируется как ошибка бд.

    """

    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Optional[Any]:

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

    return wrapper
