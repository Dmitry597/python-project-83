from urllib.parse import urlparse

import validators
from flask import current_app

from page_analyzer.models.url_repository import UrlRepository
from page_analyzer.services.parser import PageAnalyzer


def get_url_repository():
    return UrlRepository(current_app.config['DATABASE_URL'])


# def handle_new_url(url, url_repo):
#     errors = validate(url)

#     if errors:
#         message, category = errors['message'], 'danger'
#         redirect_path = 'url.home'

#         return message, category, redirect_path

#     normalize_url = '://'.join(urlparse(url)[:2])

#     message, category, id_url = url_repo.save_url(normalize_url)
#     redirect_path = 'url.show_url'

#     return message, category, redirect_path

def handle_new_url(url, url_repo):

    normalize_url = '://'.join(urlparse(url)[:2])

    info, id_url = url_repo.save_url(normalize_url)

    if info:
        message, category = 'Страница уже существует', 'info'
    else:
        message, category = 'Страница успешно добавлена', 'success'

    return message, category, id_url


def handle_checks_url(url_id, url_repo):

    info_url = url_repo.find_url(url_id)

    analyzer = PageAnalyzer(info_url['name'])

    errors = analyzer.get_page_content()

    if errors:
        message, category = errors['message'], errors['category']
    else:
        url_repo.save_checks_url(
            url_id,
            analyzer.status_code,
            analyzer.h1,
            analyzer.title,
            analyzer.description
        )
        message, category = 'Страница успешно проверена', 'success'

    return message, category


def validate(url):
    errors = {}

    if not validators.url(url):
        errors['message'] = 'Некорректный URL'

    if len(url) > 255:
        errors['message'] = 'URL превышает 255 символов'

    return errors


# def check_status_code(url):
#     errors = {}

#     try:
#         resp = requests.get(url, timeout=10)
#         resp.raise_for_status()

#     except requests.exceptions.RequestException as req_err:
#         errors['error'] = req_err
#         errors['message'] = 'Произошла ошибка при проверке'
#         errors['category'] = 'danger'

#     return errors


# def handle_checks_url(url_id, url_repo):

#     info_url = url_repo.find_url(url_id)

#     errors = check_status_code(info_url['name'])

#     if errors:
#         message, category = errors['message'], errors['category']

#     else:
#         message, category = url_repo.save_checks_url(url_id, status_code=200)

#     return message, category
