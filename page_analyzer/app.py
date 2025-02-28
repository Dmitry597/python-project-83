import os
from dotenv import load_dotenv
from page_analyzer.url_repository import UrlRepository
from page_analyzer.utils import handle_new_url, show_all_urls
from flask import (Flask,
                   abort,
                   render_template,
                   request,
                   )


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

url_repo = UrlRepository(app.config['DATABASE_URL'])


@app.route('/', methods=['GET', 'POST'])
def home():
    return render_template('home.html')


@app.route('/urls', methods=['GET', 'POST'])
def url_manager():
    if request.method == 'POST':
        return handle_new_url(url_repo)
    return show_all_urls(url_repo)


@app.route('/urls/<int:id>')
def show_url(id):
    info_url = url_repo.find_url(id)

    if not info_url:
        abort(404)
    print(info_url)

    return render_template('url_detail.html', url=info_url)


@app.errorhandler(404)
def pageNotFount(error):
    return render_template('page404.html'), 404


if __name__ == "__main__":
    app.run(debug=True)
