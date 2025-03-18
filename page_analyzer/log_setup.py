import logging
import os
import logging.config

import yaml


def setup_logging(
    config_path: str = 'logging_config.yaml',
    default_level: int = logging.INFO
) -> None:

    """
    Настройка логгера для записи в файл и в консоль.

    Функция проверяет наличие директории для логов,
    создает её при отсутствии, настраивает систему логирования с использованием
    указанного файла конфигурации.

    Если файл не найден, устанавливается уровень логирования по умолчанию
    с стандартным форматом сообщений.
    """

    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Проверяем, существует ли файл конфигурации
    if os.path.exists(config_path):
        # Загружаем конфигурацию логирования из YAML файла
        with open(config_path, 'rt') as f:
            config = yaml.safe_load(f.read())

        logging.config.dictConfig(config)
    else:
        print('NOOOO')
        # Если файл не найден, устанавливаем уровень логирования по умолчанию
        log_format = (
            "[%(asctime)s.%(msecs)03d] "
            "[%(name)-50s] "
            "[%(module)-15s:%(lineno)-3d] "
            "[%(levelname)-8s] -> "
            "%(message)s"
        )
        log_datefmt = "%Y-%m-%d %H:%M:%S"

        logging.basicConfig(
            level=default_level, format=log_format, datefmt=log_datefmt
        )
