__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Dec. 05, 2017'
__status__ = 'Active'


# imports
import paramiko
from traitsui.api import View, Item, Group, Handler, EnumEditor
from traitsui.menu import OKButton, CancelButton

import numpy as np
import pandas as pd
import traits.api as tr


# -----------------------------------------------------------------------------
# definition of classes for the different experiment types, materials, methods
# -----------------------------------------------------------------------------
class CylinderTest(tr.HasStrictTraits):
    """ Defines the Cylinder Test class """

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


class SFTPConnection(tr.HasTraits):
    """ Defines the SFTP connection class """

    # input variables
    username = tr.Str('ftp', desc="username", label="username", )

    # tr.Password hides the entered password
    password = tr.Password('', desc="password", label="password", )

    test_type = tr.Enum('Cylinder-Tests', 'Beam-End-Tests',
                        'Stress-Redistribution-Tests')

    # variables of the object(self), do not belong to the class, changeable
    # for every element
    def __init__(self):
        self.host = "bane.imb.rwth-aachen.de"
        self.port = 22

    # definition of pop-up window
    traits_view = View(Item(name='username'),
                       Item(name='password'),
                       # Item(name='test_type'),
                       buttons=[OKButton, CancelButton])

    traits_view2 = View(Item(name='test_type'),
                        buttons=[OKButton, CancelButton])

    # prints the entered username and password
    def check_inputs(self):
        print('Logged in as user: "%s"' % self.username)
        print('Requested test type: %s' % self.test_type)

    test_type_dir = tr.Property(depends_on='test_type')
    '''Top level directory for the selected test type.
    '''
    @tr.cached_property
    def _get_test_type_dir(self):
        return '/home/ftp/austausch_chudoba/%s/raw_data' % self.test_type

    test_treatments = tr.Property(depends_on='test_type')
    '''List of test treatments conducted for the currently selected test type.
    '''
    @tr.cached_property
    def _get_test_treatments(self):

        self.transport = paramiko.Transport(self.host, self.port)
        self.transport.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        file_list = self.sftp.listdir(self.test_type_dir)
        file_list_csv = []
        for names in file_list:
            if names.endswith('.csv'):
                file_list_csv.append(names)
        return sorted(file_list_csv)

    # returns the path of the local file after downloading it from the server
    def transport_file(self, test_file, test):
        self.transport = paramiko.Transport(self.host, self.port)
        self.transport.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)
        self.filepath = '/home/ftp/austausch_chudoba/%s/raw_data/%s' % (
            test_file, test)
        self.localpath = './%s' % test
        # get the raw data file from the server and store it local
        self.sftp.get(self.filepath, self.localpath)
        # return the path of the local raw data file
        return self.localpath

    def local_raw_file(self):
        # return only the path of the local raw data file created in
        # transport_file
        return self.localpath

    def disconnect(self):
        # disconnects from the ftp server
        return [self.sftp.close(), self.transport.close()]


class RequestedTest(tr.HasTraits):
    """ Defines the requested test class """

    file_list = tr.List
    selected_test = tr.Enum(values='file_list')

    # definition of pop-up window
    traits_view = View(Item(name='selected_test'),
                       buttons=[OKButton, CancelButton])

    # prints the entered test name
    def check_input(self):
        print('Requested test: %s' % self.list)
