install: # установить зависимости проекта
	poetry install

lint:
	poetry run flake8 .

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

local_start:
	poetry run flask --app page_analyzer.app --debug run --port 8000

build:
	bash ./build.sh