
import os
import sqlite3

DATABASE_PATH = os.environ.get(
    "DATABASE_PATH",
    os.path.join(os.path.dirname(__file__), "catalog.db")
)


def get_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                subject TEXT NOT NULL,
                price REAL NOT NULL,
                quantity INTEGER NOT NULL
            )
        """)

        book_count = connection.execute(
            "SELECT COUNT(*) FROM books"
        ).fetchone()[0]

        if book_count == 0:
            books = [
                (
                    "How to get a good grade in DOS in 40 minutes a day",
                    "Distributed Systems",
                    10.0,
                    10
                ),
                (
                    "RPCs for Noobs",
                    "Distributed Systems",
                    12.0,
                    10
                ),
                (
                    "Xen and the Art of Surviving Undergraduate School",
                    "Undergraduate School",
                    15.0,
                    10
                ),
                (
                    "Cooking for the Impatient Undergrad",
                    "Undergraduate School",
                    8.0,
                    10
                )
            ]

            connection.executemany("""
                INSERT INTO books (title, subject, price, quantity)
                VALUES (?, ?, ?, ?)
            """, books)
