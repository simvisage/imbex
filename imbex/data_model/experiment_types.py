__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 23, 2017'
__status__ = 'Draft'

import paramiko
from traitsui.api import View, Item, Group
from traitsui.menu import OKButton, CancelButton

import numpy as np
import pandas as pd
import traits.api as tr


# -----------------------------------------------------------------------------
# definition of classes for the different experiment types, materials, methods
# -----------------------------------------------------------------------------
# class defining the beam-end tests
class BeamEndTest(tr.HasStrictTraits):
    height = tr.Float(unit='mm')

    length = tr.Float(unit='mm')

    width = tr.Float(unit='mm')

    bond_length = tr.Float(unit='mm')

    number_longitudinal_ri = tr.Int(1)

    number_stirrup = tr.Int(1)

    traits_view = View(Group(Item(name='height'),
                             Item(name='length'),
                             Item(name='width'),
                             Item(name='bond_length'),
                             Item(name='number_longitudinal_ri'),
                             Item(name='number_stirrup'),
                             label='Beam End', show_border=True))


# class defining the reinforcement
class Reinforcement(tr.HasStrictTraits):
    diameter_long_ri = tr.Int(unit='mm')

    diameter_stirrup = tr.Int(unit='mm')

    material_long_ri = tr.Str('Steel')

    material_stirrup = tr.Str('Steel')

    category_long_ri = tr.Str('B500')

    category_stirrup = tr.Str('B500')

    strength_long_ri = tr.Float(unit='MPa')

    strength_stirrup = tr.Float(unit='MPa')


# class defining the concrete
class Concrete(tr.HasStrictTraits):
    category_c = tr.Str('C120')

    strength_c = tr.Float(unit='MPa')

    date_production = pd.to_datetime('2017-10-01')

    date_test = pd.to_datetime('2017-11-01')

    age_specimen = tr.Int(unit='d')


# class defining the cylinder tests
class CylinderTest(tr.HasStrictTraits):
    # input variables
    data = tr.Array(np.float_, input=True)

    height = tr.Float(300.0, unit='mm')

    diameter = tr.Float(100.0, unit='mm')

    category_c = tr.Str('C120')

    strength_c = tr.Float(120.0, unit='MPa')

    date_production = pd.to_datetime('2017-10-01')

    date_test = pd.to_datetime('2017-11-01')

    age_specimen = tr.Float(56.0, unit='d')

    loading_scenario = tr.Str('LS1')

    frequency = tr.Float(5.0, unit='Hz')

    loading_cycles = tr.Str(100)

    # properties / cached_properties
    argmax_force = tr.Property(depends_on='+input')

    # index of maximum force f_max
    @tr.cached_property
    def _get_argmax_force(self):
        f = self.data[:, 1]
        return np.argmin(f)

    t = tr.Property(depends_on='+input')

    # time at f_max
    @tr.cached_property
    def _get_t(self):
        return self.data[:self.argmax_force, 0]

    f = tr.Property(depends_on='+input')

    # maximum force f_max
    @tr.cached_property
    def _get_f(self):
        return -self.data[:self.argmax_force, 1]

    u = tr.Property(depends_on='+input')

    # machine displacement at f_max
    @tr.cached_property
    def _get_u(self):
        return -self.data[:self.argmax_force, 2]

    wa1 = tr.Property(depends_on='+input')

    # gauge 1 displacement at f_max
    @tr.cached_property
    def _get_wa1(self):
        return self.data[:self.argmax_force, 3]

    wa2 = tr.Property(depends_on='+input')

    # gauge 2 displacement at f_max
    @tr.cached_property
    def _get_wa2(self):
        return self.data[:self.argmax_force, 4]

    wa3 = tr.Property(depends_on='+input')

    # gauge 3 displacement at f_max
    @tr.cached_property
    def _get_wa3(self):
        return self.data[:self.argmax_force, 5]


# class for SFTP connection using paramiko
class SFTPConnection(tr.HasTraits):
    # input variables
    username = tr.Str('ftp',
                      desc="username",
                      label="username", )

    password = tr.Password(desc="password",
                           label="password", )

    # definition of pop-up window
    traits_view = View(Item(name='username'),
                       Item(name='password', style='simple', label='Password'),
                       buttons=[OKButton, CancelButton])

    # prints the entered username and password
    def check_authentication(self):
        print('Loged in as user "%s" with password "%s".' % (
            self.username, self.password))

    # returns a SFTP-Connection with given arguments
    def __init__(self, test, filepath, localpath):
        self.test = test
        self.host = "134.130.81.25"
        self.port = 22
        self.filepath = filepath
        self.localpath = localpath

    # returns the path of the local file after downloading it from the server
    def connect(self):
        global sftp
        global transport
        transport = paramiko.Transport(self.host, self.port)
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(self.filepath, self.localpath)
        return self.localpath

    # function to disconnect
    def disconnect(self):
        return [sftp.close(), transport.close()]


class RequestedTest(tr.HasTraits):
    '''class defining the requested test
    '''
    test_name = tr.Str('CT_120_1_', desc="test name",
                       label="test name", )
    '''input variable
    '''

    # definition of pop-up window
    traits_view = View(Item(name='test_name'),
                       buttons=[OKButton, CancelButton])

    # returns the global variable test
    def output_test(self):
        global test
        test = self.test_name
        return test

    # prints the entered test name
    def check_test_name(self):
        print('Requested test: %s' % self.test_name)
