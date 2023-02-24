CREATE TABLE IF NOT EXISTS "sessions" (
    "session_id"  TEXT      NOT NULL  UNIQUE,
    "username"    TEXT      NOT NULL  UNIQUE,
    "agent"       TEXT      NOT NULL,
    "time"        NUMERIC   NOT NULL
);

CREATE TABLE IF NOT EXISTS "devices" (
    "id"           INTEGER PRIMARY KEY UNIQUE,
    "name"         TEXT    NOT NULL    UNIQUE,
    "description"  TEXT    NULL,
    "type"         INT     NOT NULL,
    "options"      TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS "rules" (
    "id"           INTEGER PRIMARY KEY UNIQUE,
    "name"         TEXT    NOT NULL    UNIQUE,
    "description"  TEXT    NULL,
    "device_id"    INT     NOT NULL,
    "start_time"   INT     NOT NULL,
    "duration"     INT     NOT NULL,
    FOREIGN KEY(device_id) REFERENCES devices(id)
);

CREATE TABLE IF NOT EXISTS "users" (
    "login"        TEXT    PRIMARY KEY UNIQUE,
    "role"         INT     NOT NULL DEFAULT 0
);
