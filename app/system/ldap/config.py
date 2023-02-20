from __future__ import annotations
from dataclasses import dataclass
from os import getenv


@dataclass
class LDAPConfig:
    ldap_server: str
    ldap_port: int
    ldap_use_ssl: bool
    bind_user: str
    bind_password: str
    user_base: str

    @staticmethod
    def from_env() -> LDAPConfig:
        return LDAPConfig(
            ldap_server=getenv("LDAP_SERVER"),
            ldap_port=int(getenv("LDAP_PORT")),
            ldap_use_ssl=bool(getenv("LDAP_USE_SSL")),
            bind_user=getenv("LDAP_BIND_USER"),
            bind_password=getenv("LDAP_BIND_PASSWORD"),
            user_base=getenv("LDAP_USER_BASE")
        )
