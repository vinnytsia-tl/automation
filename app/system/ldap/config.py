from __future__ import annotations

from dataclasses import dataclass
from os import getenv


@dataclass(kw_only=True)
class LDAPConfig:
    ldap_server: str
    ldap_port: int
    ldap_use_ssl: bool
    bind_user: str
    bind_password: str
    user_base: str

    @staticmethod
    def from_env() -> LDAPConfig:
        ldap_server = getenv("LDAP_SERVER")
        if ldap_server is None:
            raise ValueError("LDAP_SERVER is not set")

        ldap_port = getenv("LDAP_PORT")
        if ldap_port is None:
            raise ValueError("LDAP_PORT is not set")

        ldap_use_ssl = getenv("LDAP_USE_SSL")
        if ldap_use_ssl is None:
            raise ValueError("LDAP_USE_SSL is not set")

        bind_user = getenv("LDAP_BIND_USER")
        if bind_user is None:
            raise ValueError("LDAP_BIND_USER is not set")

        bind_password = getenv("LDAP_BIND_PASSWORD")
        if bind_password is None:
            raise ValueError("LDAP_BIND_PASSWORD is not set")

        user_base = getenv("LDAP_USER_BASE")
        if user_base is None:
            raise ValueError("LDAP_USER_BASE is not set")

        return LDAPConfig(
            ldap_server=ldap_server,
            ldap_port=int(ldap_port),
            ldap_use_ssl=bool(ldap_use_ssl),
            bind_user=bind_user,
            bind_password=bind_password,
            user_base=user_base
        )
