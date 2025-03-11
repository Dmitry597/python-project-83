import logging

from bs4 import BeautifulSoup
import requests

from page_analyzer.logging_config import setup_logging


logger = setup_logging(
    __name__,
    level=logging.WARNING,
    console_level=logging.INFO
)


class PageAnalyzer:
    def __init__(self, url):
        self.url = url
        self.status_code = None
        self.h1 = None
        self.title = None
        self.description = None

    def get_page_content(self):
        logger.debug(
            "Класс: 'PageAnalyzer', метод: 'get_page_content'. "
            "Попытка получить контент страницы для URL: %s",
            self.url
        )
        try:
            response = requests.get(self.url, timeout=10)
            response.encoding = 'utf-8'

            response.raise_for_status()

            self.status_code = response.status_code
            logger.info(
                "Класс: 'PageAnalyzer', метод: 'get_page_content'. "
                "Успешно получен контент страницы, статус код: %s",
                self.status_code
            )

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

    def parse_page(self, page_content):
        logger.debug(
            "Класс: 'PageAnalyzer', метод: 'parse_page'. "
            "Начинаю парсинг контента страницы"
        )

        soup = BeautifulSoup(page_content, "html.parser")

        self.h1 = soup.find('h1').text if soup.find('h1') else ''
        logger.debug(
            "Класс: 'PageAnalyzer', метод: 'parse_page'. "
            "H1 заголовок (h1): '%s'",
            self.h1
        )

        self.title = soup.find('title').text if soup.find('title') else ''
        logger.debug(
            "Класс: 'PageAnalyzer', метод: 'parse_page'. "
            "Заголовок страницы (title): '%s'",
            self.title
        )

        desc_meta = soup.find('meta', attrs={'name': 'description'})
        has_content = desc_meta and 'content' in desc_meta.attrs

        self.description = desc_meta['content'] if has_content else ''
        logger.debug(
            "Класс: 'PageAnalyzer', метод: 'parse_page'. "
            "Описание страницы (description): '%s'",
            self.description
        )
