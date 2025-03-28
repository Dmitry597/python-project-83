import logging
import os
import logging.config


def setup_logging() -> None:

    """
    Настройка логгера для записи в файл и в консоль.

    Функция проверяет наличие директории для логов,
    создает её при отсутствии, настраивает систему логирования.
    """

    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Определяем конфигурацию логирования в коде
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'default': {
                'format': "[%(asctime)s.%(msecs)03d] "
                "[%(name)-50s] "
                "[%(module)-30s:%(lineno)-3d] "
                "[%(levelname)-8s] -> "
                "%(message)s",

                'datefmt': "%Y-%m-%d %H:%M:%S"
            }
        },
        'handlers': {
            'file': {
                'class': 'logging.handlers.RotatingFileHandler',
                'level': 'WARNING',
                'formatter': 'default',
                'filename': 'logs/app.log',
                'maxBytes': 10485760,  # 10 MB
                'backupCount': 10,
                'encoding': 'utf-8'
            },
            'console': {
                'class': 'logging.StreamHandler',
                'level': 'INFO',
                'formatter': 'default'
            }
        },
        'root': {
            'level': 'ERROR',
            'handlers': ['console']
        },
        'loggers': {
            'page_analyzer': {
                'level': 'DEBUG',
                'handlers': ['console', 'file'],
                'propagate': False
            },
            'werkzeug': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False
            },
            'dotenv': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False
            },
            'charset_normalizer': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False
            },
            'urllib3': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False
            },
            'requests': {
                'level': 'ERROR',
                'handlers': ['console'],
                'propagate': False
            }
        }
    }

    # Применяем конфигурацию логирования
    logging.config.dictConfig(logging_config)
