import ldap3
from .config import LDAPConfig


class LDAP():
    def __init__(self, config: LDAPConfig):
        self.config = config
        self.server = ldap3.Server(config.ldap_server, config.ldap_port, use_ssl=config.ldap_use_ssl)

    def getusers(self, search_base=None):
        if search_base is None:
            search_base = self.config.user_base

        conn = ldap3.Connection(self.server, user=self.config.bind_user,
                                password=self.config.bind_password, read_only=True, version=3)
        if not conn.bind():
            return None

        search_filter = '(&(objectCategory=person)(objectClass=user))'
        attrs = ['userPrincipalName', 'displayName']
        if not conn.search(search_base, search_filter, attributes=attrs):
            return None

        return [(entry.userPrincipalName.value, entry.displayName.value) for entry in conn.entries]

    # TODO: make a ldap query
    def getuser(self, user_principal_name, search_base=None):
        users = self.getusers(search_base=search_base)
        for (login, name) in users:
            if login == user_principal_name:
                return (login, name)
        return None

    def login(self, username, password):
        conn = ldap3.Connection(self.server, user=username, password=password)
        return conn.bind()
