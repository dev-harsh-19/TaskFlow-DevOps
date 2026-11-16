"""SQLite connection and schema helpers."""

import os
import sqlite3


def connect_db(database_path):
    """Open a SQLite connection with dictionary-like rows."""
    connection = sqlite3.connect(database_path)
    connection.row_factory = sqlite3.Row
    return connection


def init_db(database_path):
    """Create the database directory and tasks table if needed."""
    database_directory = os.path.dirname(os.path.abspath(database_path))
    os.makedirs(database_directory, exist_ok=True)

    connection = connect_db(database_path)
    try:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                status TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending', 'completed')),
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        connection.commit()
    finally:
        connection.close()
