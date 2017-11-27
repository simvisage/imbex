__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 23, 2017'
__status__ = 'Draft'

import numpy as np
import pandas as pd
import paramiko
import traits.api
from traitsui.api import View, Item, Group
from traitsui.menu import OKButton, CancelButton



# -----------------------------------------------------------------------------
# definition of classes for the different experiment types, materials, methods
# -----------------------------------------------------------------------------


class BeamEndTest(traits.api.HasStrictTraits):
    height = traits.api.Float(unit='mm')

    length = traits.api.Float(unit='mm')

    width = traits.api.Float(unit='mm')

    bond_length = traits.api.Float(unit='mm')

    number_longitudinal_ri = traits.api.Int(1)

    number_stirrup = traits.api.Int(1)

    traits_view = View(Group(Item(name='height'),
                             Item(name='length'),
                             Item(name='width'),
                             Item(name='bond_length'),
                             Item(name='number_longitudinal_ri'),
                             Item(name='number_stirrup'),
                             label='Beam End', show_border=True))


class Reinforcement(traits.api.HasStrictTraits):
    diameter_long_ri = traits.api.Int(unit='mm')

    diameter_stirrup = traits.api.Int(unit='mm')

    material_long_ri = traits.api.Str('Steel')

    material_stirrup = traits.api.Str('Steel')

    category_long_ri = traits.api.Str('B500')

    category_stirrup = traits.api.Str('B500')

    strength_long_ri = traits.api.Float(unit='MPa')

    strength_stirrup = traits.api.Float(unit='MPa')


class Concrete(traits.api.HasStrictTraits):
    category_c = traits.api.Str('C120')

    strength_c = traits.api.Float(unit='MPa')

    date_production = pd.to_datetime('2017-10-01')

    date_test = pd.to_datetime('2017-11-01')

    age_specimen = traits.api.Int(unit='d')


class CylinderTest(traits.api.HasStrictTraits):
    # -----------------------------------------------
    # input variables
    # ----------------------------------------------

    data = traits.api.Array(np.float_, input=True)

    height = traits.api.Float(300.0, unit='mm')

    diameter = traits.api.Float(100.0, unit='mm')

    category_c = traits.api.Str('C120')

    strength_c = traits.api.Float(120.0, unit='MPa')

    date_production = pd.to_datetime('2017-10-01')

    date_test = pd.to_datetime('2017-11-01')

    age_specimen = traits.api.Float(56.0, unit='d')

    loading_scenario = traits.api.Str('LS1')

    frequency = traits.api.Float(5.0, unit='Hz')

    loading_cycles = traits.api.Str(100)

    # -----------------------------------------------
    # property / cached_property
    # -----------------------------------------------

    argmax_force = traits.api.Property(depends_on='+input')

    # index of maximum force f_max
    @traits.api.cached_property
    def _get_argmax_force(self):
        f = self.data[:, 1]
        return np.argmin(f)

    t = traits.api.Property(depends_on='+input')

    # time at f_max
    @traits.api.cached_property
    def _get_t(self):
        return self.data[:self.argmax_force, 0]

    f = traits.api.Property(depends_on='+input')

    # maximum force f_max
    @traits.api.cached_property
    def _get_f(self):
        return -self.data[:self.argmax_force, 1]

    u = traits.api.Property(depends_on='+input')

    # machine displacement at f_max
    @traits.api.cached_property
    def _get_u(self):
        return -self.data[:self.argmax_force, 2]

    wa1 = traits.api.Property(depends_on='+input')

    # gauge 1 displacement at f_max
    @traits.api.cached_property
    def _get_wa1(self):
        return self.data[:self.argmax_force, 3]

    wa2 = traits.api.Property(depends_on='+input')

    # gauge 2 displacement at f_max
    @traits.api.cached_property
    def _get_wa2(self):
        return self.data[:self.argmax_force, 4]

    wa3 = traits.api.Property(depends_on='+input')

    # gauge 3 displacement at f_max
    @traits.api.cached_property
    def _get_wa3(self):
        return self.data[:self.argmax_force, 5]


# class for SFTP connection using paramiko
class SFTPConnection(traits.api.HasTraits):
    username = traits.api.Str('ftp',
                              desc="username",
                              label="username", )

    password = traits.api.Str(desc="password",
                              label="password", )

    traits_view = View(Item(name='username'),
                       Item(name='password'),
                       buttons = [OKButton, CancelButton])

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

    def disconnect(self):
        return [sftp.close(), transport.close()]


# class defining the requested test
class RequestedTest(traits.api.HasTraits):


    test_name = traits.api.Str('CT_120_1_', desc="test name",
                              label="test name", )

    traits_view = View(Item(name='test_name'),
                             buttons = [OKButton, CancelButton])

    def output_test(self):
        global test
        test = self.test_name
        return test

    def check_test_name(self):
        print('Requested test: %s' % self.test_name)