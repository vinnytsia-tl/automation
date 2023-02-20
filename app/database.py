import sqlite3
import threading


class Database():
    def __init__(self, db_path) -> None:
        self.db_path = db_path
        self.thread_local = threading.local()
        self.__create_tables_if_not_exist__()

    def __create_tables_if_not_exist__(self) -> None:
        with self.get_connection() as connection:
            cursor = connection.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "sessions" (
                    "session_id"  TEXT      NOT NULL  UNIQUE,
                    "username"    TEXT      NOT NULL  UNIQUE,
                    "agent"       TEXT      NOT NULL,
                    "time"        NUMERIC   NOT NULL
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "devices" (
                    "id"           INTEGER PRIMARY KEY UNIQUE,
                    "name"         TEXT    NOT NULL    UNIQUE,
                    "description"  TEXT    NULL,
                    "type"         INT     NOT NULL,
                    "options"      TEXT    NOT NULL
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "rules" (
                    "id"           INTEGER PRIMARY KEY UNIQUE,
                    "name"         TEXT    NOT NULL    UNIQUE,
                    "description"  TEXT    NULL,
                    "device_id"    INT     NOT NULL,
                    "start_time"   INT     NOT NULL,
                    "duration"     INT     NOT NULL,
                    FOREIGN KEY(device_id) REFERENCES devices(id)
                );
            ''')
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS "users" (
                    "login"        TEXT    PRIMARY KEY UNIQUE,
                    "role"         INT     NOT NULL DEFAULT 0
                );
            ''')

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
