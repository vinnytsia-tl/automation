from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

from app.common.ldap import User as LDAPUser
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
        ldap_users = Config.ldap_descriptor.get_users()
        cursor = Config.database.execute('SELECT "login", "role" FROM "users"')
        roles = dict[str, int](cursor.fetchall())
        return [User.from_ldap(lu, roles.get(lu.user_principal_name, 0)) for lu in ldap_users]

    @staticmethod
    def find(login: str) -> User:
        ldap_user = Config.ldap_descriptor.get_user(login)
        cursor = Config.database.execute('SELECT "role" FROM "users" WHERE "login" = ?', (ldap_user.user_principal_name,))
        row = cursor.fetchone()
        return User.from_ldap(ldap_user, 0 if row is None else row[0])

    @staticmethod
    def from_ldap(ldap_user: LDAPUser, role: int) -> User:
        return User(login=ldap_user.user_principal_name,
                    name=ldap_user.display_name,
                    role=UserRole(role))
