import logging

from flask import (
    Blueprint,
    abort,
    render_template,
    url_for,
    redirect,
    request,
    flash,
    g
)

from page_analyzer.services.utils import (
    get_url_repository,
    handle_new_url,
    handle_checks_url,
    validate
)
from page_analyzer.logging_config import setup_logging


logger = setup_logging(
    __name__,
    level=logging.WARNING,
    console_level=logging.INFO
)

url_blueprint = Blueprint('url', __name__)


@url_blueprint.before_request
def before_request():
    logger.debug("Обработчик: 'before_request'. "
                 "Инициализация репозитория URL перед запросом."
                 )
    g.url_repo = get_url_repository()


@url_blueprint.route('/', methods=['GET', 'POST'])
def home():
    logger.info("Обработчик: 'home'. Вызван метод home.")
    return render_template('home.html')


@url_blueprint.route('/urls', methods=['GET', 'POST'])
def url_manager():

    logger.info("Обработчик: 'url_manager'. Метод: '%s'", request.method)

    if request.method == 'POST':
        url = request.form['url']

        logger.debug("Обработчик: 'url_manager'. Получен URL: %s", url)

        errors = validate(url)

        if errors:
            message, category = errors['message'], 'danger'

            logger.warning(
                "Обработчик: 'url_manager'. Ошибка валидации URL: %s",
                message
            )

            flash(message, category)

            return render_template('home.html'), 422

        message, category, url_id = handle_new_url(url, g.url_repo)

        logger.info(
            "Обработчик: 'url_manager'. URL: '%s', message: '%s', ID: %s",
            url, message, url_id
        )

        flash(message, category)

        return redirect(url_for('url.show_url', id=url_id))

    all_urls = g.url_repo.show_urls()

    logger.debug("Обработчик: 'url_manager'. Показ всех URL-ов: %s", all_urls)

    return render_template('all_urls.html', urls=all_urls)


@url_blueprint.route('/urls/<int:id>', methods=['GET'])
def show_url(id):

    logger.info(
        "Обработчик: 'show_url'. Метод: '%s'. Получение URL с ID: %s",
        request.method, id
    )

    info_url = g.url_repo.find_url(id)

    if not info_url:
        logger.warning(
            "Обработчик: 'show_url'. Информация о URL с ID: '%s' не найдена.",
            id
        )
        abort(404)

    logger.info(
        "Обработчик: 'show_url'. "
        "Успешно получена информация о URL с ID: %s, информация: %s",
        id, info_url
    )

    info_checks_url = g.url_repo.find_checks_urll(id)

    logger.info(
        "Обработчик: 'show_url'. "
        "Получены данные о проверке URL с ID: %s, данные: %s",
        id, info_checks_url
    )

    return render_template(
        'url_detail.html',
        url=info_url,
        checks_url=info_checks_url
    )


@url_blueprint.route('/urls/<int:url_id>/checks', methods=['POST'])
def checks_url(url_id):

    logger.info(
        "Обработчик: 'checks_url'. Метод: '%s'. Проверка URL с ID: %s",
        request.method, url_id
    )

    message, category = handle_checks_url(url_id, g.url_repo)

    logger.info(
        "Обработчик: 'checks_url'. "
        "Результат проверки URL с ID %s: сообщение '%s', категория '%s'",
        url_id, message, category
    )

    flash(message, category)

    return redirect(url_for('url.show_url', id=url_id))


def error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(error):

        logger.error(
            "Обработчик: 'page_not_found'. "
            "Ошибка 404. Информация об ошибке: %s",
            error
        )

        return render_template('page404.html'), 404

    @app.errorhandler(Exception)
    def handle_general_exception(error):

        error_code = getattr(error, 'code', 500)

        logger.error(
            "Обработчик: 'handle_general_exception'. Произошла ошибка: %s",
            error
        )

        if error_code >= 500:

            logger.critical(
                "Обработчик: 'handle_general_exception'. "
                "Ошибка сервера с кодом %s",
                error_code
            )

            return render_template(
                'page500.html',
                error_code=error_code
            ), error_code
