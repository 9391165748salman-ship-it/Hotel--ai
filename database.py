import sqlite3
from config import Config


def get_db_connection():
    connection = sqlite3.connect(Config.DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    connection = get_db_connection()

    connection.executescript("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            room TEXT,
            role TEXT DEFAULT 'guest'
        );

        CREATE TABLE IF NOT EXISTS requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            room TEXT,
            message TEXT NOT NULL,
            department TEXT,
            priority TEXT DEFAULT 'Normal',
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            request_id INTEGER,
            department TEXT,
            description TEXT,
            status TEXT DEFAULT 'Pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS notifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            message TEXT,
            read_status INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # Demo guest
    existing = connection.execute(
        "SELECT id FROM users WHERE email = ?",
        ("guest@hotelai.com",)
    ).fetchone()

    if not existing:
        connection.execute(
            """
            INSERT INTO users (name, email, room, role)
            VALUES (?, ?, ?, ?)
            """,
            ("Salman", "guest@hotelai.com", "205", "guest")
        )

    # Demo staff
    existing_staff = connection.execute(
        "SELECT id FROM users WHERE email = ?",
        ("staff@hotelai.com",)
    ).fetchone()

    if not existing_staff:
        connection.execute(
            """
            INSERT INTO users (name, email, room, role)
            VALUES (?, ?, ?, ?)
            """,
            ("Hotel Manager", "staff@hotelai.com", "-", "staff")
        )

    connection.commit()
    connection.close()