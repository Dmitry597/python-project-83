import logging
from typing import Any, Dict

from bs4 import BeautifulSoup
import requests


# Получение логгера с именем текущего модуля для записи логов
logger = logging.getLogger(__name__)


class PageAnalyzer:
    def __init__(self, url: str):
        """
        Инициализация класса PageAnalyzer.

        Params:
            url: URL страницы, которую необходимо проанализировать.
        """

        self.url = url
        self.status_code = None
        self.h1 = None
        self.title = None
        self.description = None

    def get_page_content(self) -> Dict[str, Any]:
        """
        Получает контент страницы по заданному URL.

        Метод выполняет запрос к указанному URL и обрабатывает
        ответ, получая код статуса. В случае успеха контент страницы
        передаётся в метод для дальнейшего анализа. Если происходит
        ошибка запроса, метод возвращает словарь с информацией об
        ошибке.

        """

        logger.debug(
            "Класс: 'PageAnalyzer', метод: 'get_page_content'. "
            "Попытка получить контент страницы для URL: %s",
            self.url
        )
        try:
            # Выполняем GET-запрос к указанному URL с таймаутом в 10 секунд
            response = requests.get(self.url, timeout=10)
            response.encoding = 'utf-8'

            # Проверяем, была ли ошибка в запросе (например, 404, 500 и т.д.)
            response.raise_for_status()

            self.status_code = response.status_code
            logger.info(
                "Класс: 'PageAnalyzer', метод: 'get_page_content'. "
                "Успешно получен контент страницы, статус код: %s",
                self.status_code
            )
            # Передаем текст страницы в метод анализа
            self.parse_page(response.text)

        except requests.exceptions.RequestException as req_err:
            logger.error(
                "Класс: 'PageAnalyzer', метод: 'get_page_content'. "
                "Ошибка запроса для URL %s: %s",
                self.url, req_err
            )

            errors = {
                'error': str(req_err),
                'message': 'Произошла ошибка при проверке',
                'category': 'danger'
            }
            return errors

    def parse_page(self, page_content: str) -> None:
        """
        Парсит контент HTML страницы, извлекая заголовок H1,
        заголовок страницы (title) и описание (meta description).
        """

        logger.debug(
            "Класс: 'PageAnalyzer', метод: 'parse_page'. "
            "Начинаю парсинг контента страницы"
        )

        soup = BeautifulSoup(page_content, "html.parser")

        # Извлекаем заголовок H1
        self.h1 = soup.find('h1').text if soup.find('h1') else ''

        logger.debug(
            "Класс: 'PageAnalyzer', метод: 'parse_page'. "
            "H1 заголовок (h1): '%s'",
            self.h1
        )

        # Извлекаем заголовок страницы
        self.title = soup.find('title').text if soup.find('title') else ''

        logger.debug(
            "Класс: 'PageAnalyzer', метод: 'parse_page'. "
            "Заголовок страницы (title): '%s'",
            self.title
        )

        # Извлекаем мета-описание
        desc_meta = soup.find('meta', attrs={'name': 'description'})
        has_content = desc_meta and 'content' in desc_meta.attrs

        self.description = desc_meta['content'] if has_content else ''

        logger.debug(
            "Класс: 'PageAnalyzer', метод: 'parse_page'. "
            "Описание страницы (description): '%s'",
            self.description
        )
