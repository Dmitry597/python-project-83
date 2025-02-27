install: # установить зависимости проекта
	poetry install

# build: # позволpupu
# 	poetry build

# publish: # для отладки публикации
# 	poetry publish --dry-run

# package-install: # для установки пакета из операционной системы
# 	python3 -m pip install dist/*.whl

# package-reinstall: # для переустановки пакета из операционной системы
# 	pip install --force-reinstall dist/*.whl

# installation:
# 	poetry install
# 	poetry build
# 	poetry publish --dry-run
# 	pip install --force-reinstall dist/*.whl


lint:
	poetry run flake8 .

dev:
	poetry run flask --app page_analyzer:app run

PORT ?= 8000
start:
	poetry run gunicorn -w 5 -b 0.0.0.0:$(PORT) page_analyzer:app

local_start:
	poetry run flask --app page_analyzer.app --debug run --port 8000

build_poet:
	poetry run bash ./build.sh

build:
	bash ./build.sh