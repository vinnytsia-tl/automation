from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from app.config import Config


class UserRole(Enum):
    COMMON = 0
    RUNNER = 1
    MODERATOR = 2
    ADMIN = 3

    @staticmethod
    def cast(value: int | str | UserRole | None) -> Optional[UserRole]:
        if value is None:
            return None
        if isinstance(value, UserRole):
            return value
        if isinstance(value, int):
            return UserRole(value)
        return UserRole[value]


@dataclass
class User:
    login: Optional[str] = None
    name: Optional[str] = None
    role: Optional[UserRole] = None

    def __post_init__(self):
        self.role = UserRole.cast(self.role)

    def save(self) -> None:
        with Config.database.get_connection() as db:
            role_value = self.role.value if self.role is not None else None
            cursor = db.execute('UPDATE "users" SET "role" = ? WHERE "login" = ?', (role_value, self.login))
            if cursor.rowcount == 0:
                cursor.execute('INSERT INTO "users" ("login", "role") VALUES (?, ?)', (self.login, role_value))

    @staticmethod
    def all() -> List[User]:
        ldap_users = Config.ldap_descriptor.getusers()
        cursor = Config.database.execute('SELECT "login", "role" FROM "users"')
        roles = dict(cursor.fetchall())

        return [User(login=login, name=name, role=UserRole(roles.get(login, 0))) for (login, name) in ldap_users]

    @staticmethod
    def find(login: str) -> User:
        ldap_user = Config.ldap_descriptor.getuser(login)
        if ldap_user is None:
            raise ValueError(f"User with login {login} not found")

        login, name = ldap_user

        cursor = Config.database.execute('SELECT "role" FROM "users" WHERE "login" = ?', (login,))
        row = cursor.fetchone()
        role = UserRole.COMMON if row is None else UserRole(row[0])

        return User(login=login, name=name, role=role)
