-- Таблица urls предназначена для хранения информации о URL.
-- Поля:
-- id - уникальный идентификатор для каждой записи в таблице,
-- автоматически увеличивается (тип SERIAL).

-- name - строка, содержащая имя или URL (тип VARCHAR(255)),
-- которая не может быть пустой (NOT NULL).

-- created_at - дата и время создания записи,
-- автоматически заполняется текущей меткой времени при создании записи
-- (тип TIMESTAMP, NOT NULL, с заданным значением по умолчанию).

CREATE TABLE IF NOT EXISTS urls (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);


-- Таблица url_checks предназначена для хранения результатов проверки URL.
-- Поля:
-- id - уникальный идентификатор проверки (SERIAL PRIMARY KEY).
-- url_id - идентификатор URL, на который ссылается проверка (BIGINT, внешний ключ).
-- status_code - HTTP статус код, полученный при проверке URL (INT).
-- h1 - заголовок <h1> страницы (VARCHAR(255)).
-- title - заголовок страницы (TITLE) (VARCHAR(255)).
-- description - описание страницы (DESCRIPTION) (VARCHAR(255)).
-- created_at - дата и время создания записи (TIMESTAMP, по умолчанию текущее время).


CREATE TABLE IF NOT EXISTS url_checks (
    id SERIAL PRIMARY KEY,
    url_id BIGINT REFERENCES urls (id),
    status_code INT,
    h1 VARCHAR(255),
    title VARCHAR(255),
    description VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
