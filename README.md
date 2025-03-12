### Hexlet tests and linter status:
[![Actions Status](https://github.com/Dmitry597/python-project-83/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/Dmitry597/python-project-83/actions)

[![Python CI](https://github.com/Dmitry597/python-project-83/actions/workflows/run-flake8.yml/badge.svg)](https://github.com/Dmitry597/python-project-83/actions/workflows/run-flake8.yml)

[![Maintainability](https://api.codeclimate.com/v1/badges/4de9abb7216c54092111/maintainability)](https://codeclimate.com/github/Dmitry597/python-project-83/maintainability)

# Page analyzer:
Демо-версию сайта можно посмотреть [здесь](https://python-flask-analyzer.onrender.com).

### Project Description:

**Page Analyzer** – это сайт, который анализирует указанные страницы на SEO-пригодность по аналогии с PageSpeed Insights.

*На главной странице вы сможете ввести URL-адрес интересующего вас веб-сайта и нажать кнопку "ПРОВЕРИТЬ". Если введённый URL корректен, вы получите доступ к странице с таблицей проверок. На этой странице просто нажмите кнопку "ЗАПУСТИТЬ ПРОВЕРКУ", чтобы инициировать процесс анализа. Ваш сайт будет проверен, после чего результаты проверки отобразятся в информативной таблице.*


### Screenshots:

*Домашняя страница:*

![home](https://github.com/Dmitry597/python-project-83/blob/main/assets/photos_for_redmi/home.png) 

*Страница с таблицей всех добавленных URL-адресов:*
  
![all_urls](https://github.com/Dmitry597/python-project-83/blob/main/assets/photos_for_redmi/all_urls.png)  

*Страница с подробной информацией об URL-адресе и его проверках.*
  
![url_detail](https://github.com/Dmitry597/python-project-83/blob/main/assets/photos_for_redmi/url_detail.png)  


### Installation:

Чтобы установить и запустить проект, выполните следующие шаги:

1. **Клонируйте репозиторий:**
```bash
   git clone https://github.com/Dmitry597/python-project-83.git
   cd python-project-83
```

*Убедитесь, что у вас установлен Poetry.*

2. **Настройте переменные окружения:**

*Создайте файл **.env** в корневом каталоге проекта и добавьте в него следующие переменные:*

   - **SECRET_KEY=*{secret_key}***
   - **DATABASE_URL=*{provider}://{user}:{password}@{host}:{port}/{db}***

*Замените **{secret_key}** и остальные параметры на свои собственные значения.*

3. **Установите зависимости и сделайте сборку приложения:**

*1. Сделайте скрипт исполняемым:*

*Чтобы файл **build.sh** стал исполняемым, выполните следующую команду в терминале:*

```bash
   chmod +x ./build.sh
```

*2. Запустите скрипт* 

*После того как скрипт стал исполняемым, вы можете запустить его с помощью команды:*

```bash
   make build
```
**Эта команда:**

- *загружает переменные среды из файла .env, чтобы сделать их доступными для последующих команд в скрипте*

- *установит все необходимые зависимости, включая Flask и другие библиотеки.*

- *выполнет инициализацию базы данных с помощью команды psql, которая загружает SQL скрипт из database.sql в указанную базу данных с использованием URL, заданного в переменной DATABASE_URL.*


**Важно:** *Для успешного выполнения этого скрипта на вашем компьютере должен быть установлен и корректно настроен PostgreSQL. Убедитесь, что сервер PostgreSQL запущен и доступен для соединений.*


4. **Запустите приложение в режиме разработки:**

*Используйте следующую команду для запуска приложения:*
```bash
   make dev
```
*Это позволит вам запустить приложение в режиме разработки, который автоматически перезагрузит сервер при внесении изменений в код.*




