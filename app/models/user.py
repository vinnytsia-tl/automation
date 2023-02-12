from __future__ import annotations
from enum import Enum
from dataclasses import dataclass
from typing import List

from ..database import Database
from ..system.ldap import LDAP


class UserRole(Enum):
    COMMON = 0
    MODERATOR = 1
    ADMIN = 2


@dataclass
class User:
    login: str
    name: str
    role: UserRole

    def save(self, db: Database) -> User:
        cursor = db.cursor()
        cursor.execute('UPDATE "users" SET "role" = ? WHERE "login" = ?', (self.role.value, self.login))
        db.commit()

        if cursor.rowcount == 0:
            cursor.execute('INSERT INTO "users" ("login", "role") VALUES (?, ?)', (self.login, self.role.value))
            db.commit()

        return self

    @staticmethod
    def all(ldap: LDAP, db: Database) -> List[User]:
        ldap_users = ldap.getusers()
        if ldap_users is None:
            return None

        cursor = db.cursor()
        cursor.execute('SELECT "login", "role" FROM "users"')
        roles = dict(cursor.fetchall())

        return [User(login=login, name=name, role=UserRole(roles.get(login, 0))) for (login, name) in ldap_users]

    @staticmethod
    def find(ldap: LDAP, db: Database, login: str) -> User:
        ldap_user = ldap.getuser(login)
        if ldap_user is None:
            return None

        login, name = ldap_user

        cursor = db.cursor()
        cursor.execute('SELECT "role" FROM "users" WHERE "login" = ?', (login,))
        row = cursor.fetchone()
        role = UserRole.COMMON if row is None else UserRole(row[0])

        return User(login=login, name=name, role=role)
