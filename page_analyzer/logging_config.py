import logging
import os
from logging.handlers import RotatingFileHandler


def setup_logging(
    name: str,
    log_file: str = 'app.log',
    level: int = logging.INFO,
    console_level: int = logging.INFO
) -> logging.Logger:

    """
    Настройка логгера для записи в файл и в консоль.

    Params:
        name: Имя логгера, которое будет использоваться для идентификации.
        log_file: Имя файла, в который будут записываться логи.
        level: Уровень логирования для записи в файл.
        console_level: Уровень логирования для вывода в консоль.
    """

    # Создание директории для логов, если её нет
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Получение логгера
    logger = logging.getLogger(name)
    if not logger.hasHandlers():  # noqa Проверяем, есть ли уже обработчики для данного логгера 
        logger.setLevel(level)

        # Создание обработчика для записи логов в файл с ротацией
        file_handler = RotatingFileHandler(
            os.path.join('logs', log_file),
            maxBytes=10 * 1024 * 1024,  # Максимальный размер файла лога (10 MB)
            backupCount=10,  # Количество резервных копий
            encoding='utf-8')
        file_handler.setLevel(level)

        # Создание обработчика для вывода логов в консоль
        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)

        # Определение формата логирования
        formatter = logging.Formatter(
            "[%(asctime)s.%(msecs)03d] "
            "[%(name)-50s] "
            "[%(module)-15s:%(lineno)-3d] "
            "[%(levelname)-8s] -> %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # Добавление обработчиков к логгеру
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
