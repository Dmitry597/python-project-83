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
                cursor.execute("SELECT * FROM urls ORDER BY created_at DESC")
                return cursor.fetchall()

    def save_url(self, url_data):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                query = "SELECT id FROM urls WHERE name = %s LIMIT 1;"
                cursor.execute(query, (url_data,))
                url_id = cursor.fetchone()

                if url_id:
                    return ('Страница уже существуета', 'info', url_id[0])

                query = """
                    INSERT INTO urls (name, created_at)
                    VALUES (%s, %s)
                    RETURNING id
                """

                cursor.execute(query, (url_data, datetime.now()))

                url_id = cursor.fetchone()[0]

            conn.commit()

        return ('Страница успешно добавлена', 'success', url_id)
