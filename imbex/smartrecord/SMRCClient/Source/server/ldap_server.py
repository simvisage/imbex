"""
.. module: ldap_users
.. moduleauthor: Marcel Kennert
"""

from base64 import b64decode

from ldap import open, SCOPE_SUBTREE
from traits.api import HasTraits, Instance, Str, Bool
from traitsui.api import View, UItem

from basic_modules.basic_classes import Combobox
from logging import getLogger


class LDAPUsers(HasTraits):

    ldap_address = Str("134.130.81.31")

    admin_ldap = Str("Y249YWRtaW4sIGRjPWltYiwgZGM9cnd0aC1hYWNoZW4sIGRjPWRl")

    password_ldap = Str("IW1iMUBMRDY=")

    users = Instance(Combobox, ())
    
    logger=getLogger("Application")
    
    no_users=Bool(True)
    
    def __init__(self):
        try:
            users = self.get_all_active()
            for user in users:
                self.users.add_item(user, user.lower())
            self.no_users=False
        except Exception:
            self.logger.error("No connection with the LDAP-Server")

    def get_all_active(self):
        """Returns all usernames which have a active email."""
        baseDN = "ou=People, dc=imb, dc=rwth-aachen, dc=de"
        query = "(&(mail=*@imb.rwth-aachen.de)(mailAccountActive=TRUE))"
        conn = open(self.ldap_address)
        conn.simple_bind_s(b64decode(self.admin_ldap),
                           b64decode(self.password_ldap))
        res = conn.search_s(baseDN, SCOPE_SUBTREE, query)
        users = [r[1]['mail'][0].split('@')[0] for r in res]
        users.sort()
        return users
    
    def get_user(self):
        if self.no_users:
            users = self.get_all_active()
            for user in users:
                self.users.add_item(user, user.lower())
            self.no_users=False
        return self.users.get_selected_value()
    
    def show_user(self, user):
        self.users.show_value(user)
    
    view = View(
        UItem('users', style='custom', enabled_when='not no_users')
    )
