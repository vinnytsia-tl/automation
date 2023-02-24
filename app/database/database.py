import sqlite3
import threading


class Database():
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path
        self.thread_local = threading.local()

    def get_connection(self) -> sqlite3.Connection:
        try:
            return self.thread_local.connection
        except AttributeError:
            connection = sqlite3.connect(self.db_path)
            connection.execute('PRAGMA foreign_keys = ON;')
            self.thread_local.connection = connection
            return connection

    def execute(self, sql: str, params: tuple = ()) -> sqlite3.Cursor:
        return self.get_connection().execute(sql, params)

    def cleanup(self) -> None:
        with self.get_connection() as connection:
            connection.execute('DELETE FROM sessions;')
