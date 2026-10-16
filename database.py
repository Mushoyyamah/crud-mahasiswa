import sqlite3
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "mahasiswa.db"


def get_db_connection():
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_db_connection() as connection:
        connection.execute("""
            CREATE TABLE IF NOT EXISTS mahasiswa (
                nim INTEGER PRIMARY KEY,
                nama TEXT NOT NULL
                    CHECK (length(trim(nama)) > 0),
                program_studi TEXT NOT NULL
                    CHECK (length(trim(program_studi)) > 0),
                angkatan INTEGER NOT NULL,
                ipk REAL NOT NULL
                    CHECK (ipk >= 0 AND ipk <= 4)
            )
        """)