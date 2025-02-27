import os
import validators
from dotenv import load_dotenv
from page_analyzer.url_repository import UrlRepository
from urllib.parse import urlparse
from flask import (Flask,
                   abort,
                   render_template,
                   request,
                   redirect,
                   url_for,
                   flash)


load_dotenv()


app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

url_repo = UrlRepository(app.config['DATABASE_URL'])


@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        url = request.form['url']
        errors = validate(url)

        if errors:
            print('ERROR', errors)
            print('ERROR message', errors['message'])
            flash(errors['message'], 'danger')
            return redirect(url_for('home'))

        normalize_url = '://'.join(urlparse(url)[:2])
        print('url', url)
        print('normalize_url', normalize_url)

        message, categori, id_url = url_repo.save_url(normalize_url)
        print('message', message)
        print('id_url', id_url)
        flash(message, categori)
        return redirect('/')

    return render_template('home.html')


@app.route('/urls')
def show_all_urls():
    all_urls = url_repo.show_urls()
    print(all_urls)
    return render_template('all_urls.html', urls=all_urls)


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


def validate(url):
    errors = {}

    if not validators.url(url):
        errors['message'] = 'Некорректный URL'

    if len(url) > 255:
        errors['message'] = 'URL превышает 255 символов'

    return errors


# @app.route('/')
# def index():
#     return render_template('home.html')


# @app.post('/')
# def add_url():
#     url = request.form['url']

#     is_valid = validators.url(url)

#     if not is_valid:
#         print('ERROR', is_valid)
#         flash('Некорректный URL', 'error')

#         return redirect(url_for('index'))

#     normalize_url = '://'.join(urlparse(url)[:2])

#     print('url', url)
#     print('normalize_url', normalize_url)

#     message, id_url = url_repo.save_url(normalize_url)
#     print('message', message)
#     flash(message, 'success')

#     return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
