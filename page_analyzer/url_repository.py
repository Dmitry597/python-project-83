import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime


class UrlRepository:
    def __init__(self, db_url):
        self.db_url = db_url

    def get_connection(self):
        return psycopg2.connect(self.db_url)

    def save(self, url_data):
        with self.get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO urls (name, created_at) VALUES (%s, %s) "
                    "RETURNING id",
                    (url_data, datetime.now()))
                url_id = cursor.fetchone()[0]

            conn.commit()
        return url_id
