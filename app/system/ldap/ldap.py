import ldap3


class LDAP():
    def __init__(self, ldap_server, ldap_port, ldap_use_ssl, bind_user, bind_password):
        self.bind_user = bind_user
        self.bind_password = bind_password
        self.server = ldap3.Server(ldap_server, ldap_port, use_ssl=ldap_use_ssl)

    def getusers(self, search_base):
        conn = ldap3.Connection(self.server, user=self.bind_user, password=self.bind_password, read_only=True, version=3)
        if not conn.bind():
            return None

        search_filter = '(&(objectCategory=person)(objectClass=user))'
        attrs = ['userPrincipalName', 'displayName']
        if not conn.search(search_base, search_filter, attributes=attrs):
            return None

        return [{"name": entry.displayName.value, "login": entry.userPrincipalName.value} for entry in conn.entries]

    def login(self, username, password):
        conn = ldap3.Connection(self.server, user=username, password=password)
        return conn.bind()
