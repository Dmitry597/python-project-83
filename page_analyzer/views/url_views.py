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


# Настраиваем логирование для текущего модуля
logger = setup_logging(
    __name__,  # Имя логгера будет соответствовать имени текущего модуля
    level=logging.WARNING,  # Устанавливаем уровень логирования для файла
    console_level=logging.INFO  # Устанавливаем уровень логирования для консоли
)

url_blueprint = Blueprint('url', __name__)


@url_blueprint.before_request
def before_request():
    """
    Функция, выполняемая перед каждым запросом к маршрутам.
    Она создает экземпляр репозитория URL
    и сохраняет его в глобальном контексте g.
    """

    logger.debug("Обработчик: 'before_request'. "
                 "Инициализация репозитория URL перед запросом."
                 )
    # Получаем репозиторий URL для использования в других функциях.
    g.url_repo = get_url_repository()


@url_blueprint.route('/', methods=['GET'])
def home():
    """
    Главная страница. Обрабатывает запросы GET.
    На GET-запрос возвращает шаблон домашней страницы.
    """

    logger.info("Обработчик: 'home'. Вызван метод home.")
    return render_template('home.html')


@url_blueprint.route('/urls', methods=['GET', 'POST'])
def url_manager():
    """
    Менеджер URL-ов. Обрабатывает запросы GET и POST.

    На POST-запрос:
    1. Извлекает URL из формы.
    2. Проверяет URL-адрес и проверяет наличие ошибок.
    3. Если есть ошибки, формирует сообщение об ошибке
    и отображает его пользователю.
    4. Если URL корректен и успешно сохранен,
    перенаправляет на страницу отображения URL.

    На GET-запрос возвращает шаблон со списком всех URL-ов.
    """

    logger.info("Обработчик: 'url_manager'. Метод: '%s'", request.method)

    if request.method == 'POST':
        url = request.form['url']  # Извлекаем URL из формы.

        logger.debug("Обработчик: 'url_manager'. Получен URL: %s", url)
        # Проверяем валидность URL.
        errors = validate(url)

        if errors:
            message, category = errors['message'], 'danger'

            logger.warning(
                "Обработчик: 'url_manager'. Ошибка валидации URL: %s",
                message
            )

            flash(message, category) # noqa Отображаем сообщение об ошибке пользователю

            return render_template('home.html'), 422 # noqa Возвращаем домашнюю страницу с ошибками.

        # Если ошибок нет, обрабатываем полученный из формы URL.
        message, category, url_id = handle_new_url(url, g.url_repo)

        logger.info(
            "Обработчик: 'url_manager'. URL: '%s', message: '%s', ID: %s",
            url, message, url_id
        )

        flash(message, category) # noqa Отображаем сообщение об успешном добавлении пользователю

        return redirect(url_for('url.show_url', id=url_id)) # noqa Перенаправляем на страницу с полученным из формы URL.

    all_urls = g.url_repo.show_urls()  # noqa На GET-запрос выводим все существующие URL-ы.

    logger.debug("Обработчик: 'url_manager'. Показ всех URL-ов: %s", all_urls)

    return render_template('all_urls.html', urls=all_urls) # noqa Возвращаем шаблон со списком URL-ов.


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

    info_url = g.url_repo.find_url(id) # noqa Пытаемся найти URL с указанным идентификатором

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
    """
    Обработчик для выполнения проверки URL по его ID.
    """

    logger.info(
        "Обработчик: 'checks_url'. Метод: '%s'. Проверка URL с ID: %s",
        request.method, url_id
    )
    # Вызываем функцию проверки URL и получаем сообщение о результате
    message, category = handle_checks_url(url_id, g.url_repo)

    logger.info(
        "Обработчик: 'checks_url'. "
        "Результат проверки URL с ID %s: сообщение '%s', категория '%s'",
        url_id, message, category
    )

    flash(message, category)
    # Перенаправляем на страницу с деталями проверяемого URL
    return redirect(url_for('url.show_url', id=url_id))


def error_handlers(app):
    """
    Регистрация обработчиков ошибок для приложения Flask.

    Обработчики ошибок позволяют управлять ситуациями, когда возникают
    ошибки, такие как 404 (страница не найдена) и общие исключения.

    param:
          Экземпляр приложения Flask, для которого регистрируются обработчики.
    """

    @app.errorhandler(404)
    def page_not_found(error):
        """
        Обработчик для ошибок 404 (страница не найдена).

        При возникновении ошибки 404, этот обработчик
        отобразит специальную страницу для пользователей.

        Param:
                Информация об ошибке 404.
        Return:
                Страницу для отображения ошибки 404 и статус код 404.
        """

        logger.error(
            "Обработчик: 'page_not_found'. "
            "Ошибка 404. Информация об ошибке: %s",
            error
        )

        return render_template('page404.html'), 404

    @app.errorhandler(Exception)
    def handle_general_exception(error):
        """
        Обработчик для всех остальных исключений.

        При возникновении ошибок 5.., этот обработчик
        отобразит специальную страницу для пользователей.

        Param:
                Общее исключение, которое было вызвано.
        Return:
                Страницу для отображения ошибки 5.. и статус кода ошибки,
                если это ошибка сервера.

        """

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
