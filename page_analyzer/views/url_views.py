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
    handle_checks_url
)


url_blueprint = Blueprint('url', __name__)


@url_blueprint.before_request
def before_request():
    g.url_repo = get_url_repository()


@url_blueprint.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@url_blueprint.route('/urls', methods=['GET', 'POST'])
def url_manager():

    if request.method == 'POST':
        message, category, redirect_path = handle_new_url(
            request.form['url'],
            g.url_repo
        )

        flash(message, category)

        return redirect(url_for(redirect_path))

    all_urls = g.url_repo.show_urls()

    return render_template('all_urls.html', urls=all_urls)


@url_blueprint.route('/urls/<int:id>', methods=['GET'])
def show_url(id):

    info_url = g.url_repo.find_url(id)

    if not info_url:
        abort(404)

    info_checks_url = g.url_repo.find_checks_urll(id)

    return render_template(
        'url_detail.html',
        url=info_url,
        checks_url=info_checks_url
    )


@url_blueprint.route('/urls/<int:url_id>/checks', methods=['POST'])
def checks_url(url_id):

    message, category = handle_checks_url(url_id, g.url_repo)

    flash(message, category)

    return redirect(url_for('url.show_url', id=url_id))


def error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('page404.html'), 404

    @app.errorhandler(Exception)
    def handle_general_exception(error):
        error_code = getattr(error, 'code', 500)

        if error_code >= 500:
            return render_template(
                'page500.html',
                error_code=error_code
            ), error_code
