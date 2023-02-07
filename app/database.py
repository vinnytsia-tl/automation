import sqlite3
import threading


class Database():
    def __init__(self, db_path) -> None:
        self.db_path = db_path
        self.thread_local = threading.local()
        self.__create_tables_if_not_exist__()

    def __create_tables_if_not_exist__(self) -> None:
        cursor = self.cursor()
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
                "duration"     INT     NOT NULL
            );
        ''')
        self.commit()

    def __connection__(self) -> sqlite3.Connection:
        try:
            return self.thread_local.connection
        except AttributeError:
            self.thread_local.connection = sqlite3.connect(self.db_path)
            return self.thread_local.connection

    def cursor(self) -> sqlite3.Cursor:
        return self.__connection__().cursor()

    def commit(self) -> None:
        self.__connection__().commit()

    def cleanup(self) -> None:
        cursor = self.cursor()
        cursor.execute("DELETE FROM sessions;")
        self.commit()
