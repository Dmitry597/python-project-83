
from flask import (Blueprint,
                   abort,
                   render_template,
                   request,
                   g)

from page_analyzer.services.utils import (get_url_repository,
                                          handle_new_url,
                                          show_all_urls)


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
        return handle_new_url(g.url_repo)
    return show_all_urls(g.url_repo)


@url_blueprint.route('/urls/<int:id>')
def show_url(id):

    info_url = g.url_repo.find_url(id)

    if not info_url:
        abort(404)

    return render_template('url_detail.html', url=info_url)


def error_handlers(app):
    @app.errorhandler(404)
    def page_not_found(error):
        return render_template('page404.html'), 404

# @url_blueprint.errorhandler(404)
# def pageNotFount(error):
#     return render_template('page404.html'), 404
