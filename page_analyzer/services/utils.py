from urllib.parse import urlparse

import validators
import requests
from flask import current_app

from page_analyzer.models.url_repository import UrlRepository


def get_url_repository():
    return UrlRepository(current_app.config['DATABASE_URL'])


def handle_new_url(url, url_repo):
    errors = validate(url)

    if errors:
        message, category = errors['message'], 'danger'
        redirect_path = 'url.home'

        return message, category, redirect_path

    normalize_url = '://'.join(urlparse(url)[:2])

    message, category, id_url = url_repo.save_url(normalize_url)
    redirect_path = 'url.url_manager'

    return message, category, redirect_path


def handle_checks_url(url_id, url_repo):

    info_url = url_repo.find_url(url_id)

    errors = check_status_code(info_url['name'])

    if errors:
        message, category = errors['message'], errors['category']

    else:
        message, category = url_repo.save_checks_url(url_id, status_code=200)

    return message, category


def validate(url):
    errors = {}

    if not validators.url(url):
        errors['message'] = 'Некорректный URL'

    if len(url) > 255:
        errors['message'] = 'URL превышает 255 символов'

    return errors


def check_status_code(url):
    errors = {}

    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()

    except requests.exceptions.RequestException as req_err:
        errors['error'] = req_err
        errors['message'] = 'Произошла ошибка при проверке'
        errors['category'] = 'danger'

    return errors
