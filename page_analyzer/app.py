import os

from flask import Flask
from dotenv import load_dotenv

from page_analyzer.views.url_views import error_handlers, url_blueprint


load_dotenv()


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
    app.config['DATABASE_URL'] = os.getenv('DATABASE_URL')

    app.register_blueprint(url_blueprint)

    error_handlers(app)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
