__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 24, 2017'
__status__ = 'Draft'

from traits.api import *
from traitsui.api import *

class Auth(HasStrictTraits):

    username = Str(desc="username",
        label="username", )

    password = Str(desc="password",
        label="password", )

    def output(self):
        print('Login as user "%s" with password "%s".' %(
                self.username, self.password))

if __name__ == '__main__':

    Au = Auth()

    Au.configure_traits()

    Au.output()

