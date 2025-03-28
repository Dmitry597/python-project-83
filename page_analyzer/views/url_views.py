import logging

from flask import (
    Blueprint,
    abort,
    current_app,
    render_template,
    url_for,
    redirect,
    request,
    flash
)

from page_analyzer.services.utils import (
    handle_new_url,
    handle_checks_url,
    validate
)


# Получение логгера с именем текущего модуля для записи логов
logger = logging.getLogger(__name__)

url_blueprint = Blueprint('url', __name__)


@url_blueprint.route('/', methods=['GET'])
def home():
    """
    Главная страница. Обрабатывает запросы GET.
    На GET-запрос возвращает шаблон домашней страницы.
    """

    logger.info("Обработчик: 'home'. Вызван метод home.")
    return render_template('home.html')


@url_blueprint.route('/urls', methods=['GET'])
def get_url():
    """
    Обработчик для получения и отображения всех сохранённых URL.

    Этот метод принимает GET-запросы и извлекает из репозитория
    все URL-адреса, которые были сохранены ранее.
    """

    logger.info("Обработчик: 'get_urls'. Метод: 'GET'")

    all_urls = current_app.url_repo.show_urls()  # noqa На GET-запрос выводим все существующие URL-ы.

    logger.debug("Обработчик: 'get_urls'. Показ всех URL-ов: %s", all_urls)

    return render_template('all_urls.html', urls=all_urls)  # noqa Возвращаем шаблон со списком URL-ов


@url_blueprint.route('/urls', methods=['POST'])
def post_url():
    """
    Обработчик для обработки POST-запроса на добавление нового URL.

    1. Извлекает URL из формы.
    2. Проверяет URL-адрес и проверяет наличие ошибок.
    3. Если есть ошибки, формирует сообщение об ошибке
    и отображает его пользователю.
    4. Если URL корректен и успешно сохранен,
    перенаправляет на страницу отображения URL.

    """
    logger.info("Обработчик: 'post_url'. Метод: 'POST'")

    url = request.form['url']  # Извлекаем URL из формы.
    logger.debug("Обработчик: 'post_url'. Получен URL: %s", url)

    # Проверяем валидность URL.
    errors = validate(url)

    if errors:
        message, category = errors['message'], 'danger'

        logger.info("Обработчик: 'post_url'. Ошибка валидации URL: %s", message)

        flash(message, category)  # Отображаем сообщение об ошибке пользователю

        return render_template('home.html'), 422  # noqa Возвращаем домашнюю страницу с ошибками.

    # Если ошибок нет, обрабатываем полученный из формы URL.
    message, category, url_id = handle_new_url(url, current_app.url_repo)

    logger.info(
        "Обработчик: 'url_manager'. URL: '%s', message: '%s', ID: %s",
        url, message, url_id
    )

    flash(message, category) # noqa Отображаем сообщение об успешном добавлении пользователю

    return redirect(url_for('url.show_url', id=url_id))  # noqa Перенаправляем на страницу с полученным из формы URL.


@url_blueprint.route('/urls/<int:id>', methods=['GET'])
def show_url(id):
    """
    Обработчик для отображения деталей URL по его ID.

    Возвращает шаблон с информацией о URL и его проверках, если URL найден,
    в противном случае возвращается ошибка 404.

    """

    logger.info(
        "Обработчик: 'show_url'. Метод: '%s'. Получение URL с ID: %s",
        request.method, id
    )

    info_url = current_app.url_repo.find_url(id) # noqa Пытаемся найти URL с указанным идентификатором

    if not info_url:
        logger.warning(
            "Обработчик: 'show_url'. Информация о URL с ID: '%s' не найдена.",
            id
        )
        abort(404)  # Если URL не найден, возвращаем ошибку 404.

    logger.info(
        "Обработчик: 'show_url'. "
        "Успешно получена информация о URL с ID: %s, информация: %s",
        id, info_url
    )
    # Получаем данные о проверках для данного URL
    info_checks_url = current_app.url_repo.find_checks_urll(id)

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
    """
    Обработчик для выполнения проверки URL по его ID.
    """

    logger.info(
        "Обработчик: 'checks_url'. Метод: '%s'. Проверка URL с ID: %s",
        request.method, url_id
    )
    # Вызываем функцию проверки URL и получаем сообщение о результате
    message, category = handle_checks_url(url_id, current_app.url_repo)

    logger.info(
        "Обработчик: 'checks_url'. "
        "Результат проверки URL с ID %s: сообщение '%s', категория '%s'",
        url_id, message, category
    )

    flash(message, category)
    # Перенаправляем на страницу с деталями проверяемого URL
    return redirect(url_for('url.show_url', id=url_id))
