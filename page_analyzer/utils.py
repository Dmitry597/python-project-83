from urllib.parse import urlparse
import validators
from flask import (render_template,
                   request,
                   redirect,
                   url_for,
                   flash)


def handle_new_url(url_repo):
    url = request.form['url']
    errors = validate(url)

    if errors:
        flash(errors['message'], 'danger')
        return redirect(url_for('home'))

    normalize_url = '://'.join(urlparse(url)[:2])
    message, category, id_url = url_repo.save_url(normalize_url)
    flash(message, category)
    return redirect(url_for('url_manager'))


def show_all_urls(url_repo):
    all_urls = url_repo.show_urls()
    return render_template('all_urls.html', urls=all_urls)


def validate(url):
    errors = {}

    if not validators.url(url):
        errors['message'] = 'Некорректный URL'

    if len(url) > 255:
        errors['message'] = 'URL превышает 255 символов'

    return errors
