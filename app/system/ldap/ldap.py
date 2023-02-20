import logging
import ldap3

from .config import LDAPConfig

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

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
            logger.error('LDAP bind failed with user %s', self.config.bind_user)
            return None

        search_filter = '(&(objectCategory=person)(objectClass=user))'
        attrs = ['userPrincipalName', 'displayName']
        if not conn.search(search_base, search_filter, attributes=attrs):
            logger.error('No LDAP entries found for search base %s and filter %s', search_base, search_filter)
            return None

        entries = conn.entries
        logger.info('Found %d LDAP entries for search base %s and filter %s', len(entries), search_base, search_filter)
        return [(entry.userPrincipalName.value, entry.displayName.value) for entry in entries]

    # TODO: make a ldap query
    def getuser(self, user_principal_name, search_base=None):
        users = self.getusers(search_base=search_base)
        if users is None:
            return None

        for (login, name) in users:
            if login == user_principal_name:
                return (login, name)

        logger.warning('No LDAP entry found for user %s in search base %s', user_principal_name, search_base)
        return None

    def login(self, username, password):
        conn = ldap3.Connection(self.server, user=username, password=password)
        if not conn.bind():
            logger.warning("LDAP bind failed with user %s", username)
            return False

        return True
