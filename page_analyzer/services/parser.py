from bs4 import BeautifulSoup
import requests


class PageAnalyzer:
    def __init__(self, url):
        self.url = url
        self.status_code = None
        self.h1 = None
        self.title = None
        self.description = None

    def get_page_content(self):
        try:
            response = requests.get(self.url)
            response.encoding = 'utf-8'

            response.raise_for_status()

            self.status_code = response.status_code

            self.parse_page(response.text)

        except requests.exceptions.RequestException as req_err:
            errors = {
                'error': str(req_err),
                'message': 'Произошла ошибка при проверке',
                'category': 'danger'
            }
            return errors

    def parse_page(self, page_content):
        soup = BeautifulSoup(page_content, "html.parser")

        self.h1 = soup.find('h1').text if soup.find('h1') else ''

        self.title = soup.find('title').text if soup.find('title') else ''

        desc_meta = soup.find('meta', attrs={'name': 'description'})
        has_content = desc_meta and 'content' in desc_meta.attrs

        self.description = desc_meta['content'] if has_content else ''
