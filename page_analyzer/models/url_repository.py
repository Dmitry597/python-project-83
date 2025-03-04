import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime


class UrlRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def find_url(self, id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = "SELECT * FROM urls WHERE id = %s"
                cursor.execute(query, (id,))
                return cursor.fetchone()

    def show_urls(self):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    SELECT
                        urls.id,
                        urls.name,
                        url_checks.status_code,
                        url_checks.created_at,
                        urls.created_at AS url_created_at
                    FROM
                        urls
                    LEFT JOIN
                        url_checks ON urls.id = url_checks.url_id
                        AND url_checks.created_at = (
                            SELECT MAX(created_at)
                            FROM url_checks
                            WHERE urls.id = url_checks.url_id
                        )
                    ORDER BY
                        urls.created_at DESC;
                """
                cursor.execute(query)
                return cursor.fetchall()

    def save_url(self, url_data):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT id FROM urls WHERE name = %s LIMIT 1;"
                cursor.execute(query, (url_data,))
                url_id = cursor.fetchone()

                if url_id:
                    return 'Страница уже существует', 'info', url_id[0]

                query = """
                    INSERT INTO urls (name, created_at)
                    VALUES (%s, %s)
                    RETURNING id
                """

                cursor.execute(query, (url_data, datetime.now()))

                url_id = cursor.fetchone()[0]

            conn.commit()

        return 'Страница успешно добавлена', 'success', url_id

    def save_checks_url(self, url_id, status_code):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                    INSERT INTO url_checks (url_id, status_code, created_at)
                    VALUES (%s, %s, %s)
                """

                cursor.execute(query, (url_id, status_code, datetime.now()))

                return 'Страница успешно проверена', 'success'

    def find_checks_urll(self, url_id):
        with self.get_connection() as conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                query = """
                        SELECT * FROM url_checks
                        WHERE url_id = %s
                        ORDER BY created_at DESC;
                    """
                cursor.execute(query, (url_id,))
                return cursor.fetchall()
