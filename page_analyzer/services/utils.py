from urllib.parse import urlparse

import validators
from flask import (current_app)

from page_analyzer.models.url_repository import UrlRepository


def get_url_repository():
    return UrlRepository(current_app.config['DATABASE_URL'])


def handle_new_url(url, url_repo):
    errors = validate(url)

    if errors:
        return errors['message'], 'danger', 'url.home'

    normalize_url = '://'.join(urlparse(url)[:2])
    message, category, id_url = url_repo.save_url(normalize_url)

    return message, category, 'url.url_manager'


def validate(url):
    errors = {}

    if not validators.url(url):
        errors['message'] = 'Некорректный URL'

    if len(url) > 255:
        errors['message'] = 'URL превышает 255 символов'

    return errors
