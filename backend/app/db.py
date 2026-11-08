import psycopg2
from psycopg2.extras import RealDictCursor

from app.config import DB_HOST, DB_NAME, DB_PASS, DB_PORT, DB_USER


def get_conn():
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASS,
        dbname=DB_NAME,
        cursor_factory=RealDictCursor,
    )
    try:
        yield conn
    finally:
        conn.close()