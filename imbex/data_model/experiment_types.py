__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 23, 2017'
__status__ = 'Draft'


# imports
import numpy as np
import pandas as pd
import paramiko
import traits.api as tr
from traitsui.api import View, Item, Group, Handler, EnumEditor
from traitsui.menu import OKButton, CancelButton


# -----------------------------------------------------------------------------
# definition of classes for the different experiment types, materials, methods
# -----------------------------------------------------------------------------


class BeamEndTest(tr.HasStrictTraits):
    """ Defines the Beam-End test class """

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


class Reinforcement(tr.HasStrictTraits):
    """ Defines the Reinforcement class """

    diameter_long_ri = tr.Int(unit='mm')

    diameter_stirrup = tr.Int(unit='mm')

    material_long_ri = tr.Str('Steel')

    material_stirrup = tr.Str('Steel')

    category_long_ri = tr.Str('B500')

    category_stirrup = tr.Str('B500')

    strength_long_ri = tr.Float(unit='MPa')

    strength_stirrup = tr.Float(unit='MPa')


class Concrete(tr.HasStrictTraits):
    """ Defines the Concrete class """

    category_c = tr.Str('C120')

    strength_c = tr.Float(unit='MPa')

    date_production = pd.to_datetime('2017-10-01')

    date_test = pd.to_datetime('2017-11-01')

    age_specimen = tr.Int(unit='d')


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
    password = tr.Password('!mb1@FTP7', desc="password", label="password", )

    test_types = tr.Enum('Cylinder-Tests', 'Beam-End-Tests', 'Stress-Redistribution-Tests')

    # definition of pop-up window
    traits_view = View(Item(name='username'),
                       Item(name='password'),
                       Item(name='test_types'),
                       buttons=[OKButton, CancelButton])

    # prints the entered username and password
    def check_inputs(self):
        print('Logged in as user: "%s"' % self.username)
        print('Requested test type: %s' % self.test_types)

    def output_test_type(self):
        return self.test_types

    def requested_directory(self):
        return '/home/ftp/austausch_chudoba/%s/raw_data' % self.test_types

    # variables of the object(self), do not belong to the class, changeable for every element
    def __init__(self):
        self.host = "134.130.81.25"
        self.port = 22
        self.transport = paramiko.Transport(self.host, self.port)
        self.transport.connect(username=self.username, password=self.password)
        self.sftp = paramiko.SFTPClient.from_transport(self.transport)

    def list_files(self, directory):
        self.directory = directory
        self.file_list = self.sftp.listdir(self.directory)
        return self.file_list

    # returns the path of the local file after downloading it from the server
    def transport_file(self, test_file, test):
        self.filepath = '/home/ftp/austausch_chudoba/%s/raw_data/%s' %(test_file, test)
        self.localpath = './%s' % test
        # get the raw data file from the server and store it local
        self.sftp.get(self.filepath, self.localpath)
        # return the path of the local raw data file
        return self.localpath

    def local_raw_file(self):
        # return only the path of the local raw data file created in transport_file
        return self.localpath

    def disconnect(self):
        # disconnects from the ftp server
        return [self.sftp.close(), self.transport.close()]


class RequestedTest(tr.HasTraits):
    """ Defines the requested test class """

    file_list = ()
    list = tr.Enum(values='file_list')

    # definition of pop-up window
    traits_view = View(Item(name='list'),
                       buttons=[OKButton, CancelButton])

    # returns the global variable test
    def output_test(self):
        return self.list

    # prints the entered test name
    def check_input(self):
        print('Requested test: %s' % self.list)



# class TestType(tr.HasTraits):
#     ''' class for dynamic redefinition of test list
#     '''
#     CT_list = tr.List()
#     BE_list = tr.List()
#     SR_list = tr.List()
#
#     test_type_list = {
#         'Cylinder Tests': CT_list,
#         'Beam-End Tests': BE_list,
#         'Stress-Redistribution Tests': SR_list
#     }
#     test_type = tr.Enum(list(test_type_list())[0], list(test_type_list()))
#     test = tr.Str
#
#     view = View(
#         Item(name='test_type_list'),
#         Item(name='test',
#              editor=EnumEditor(name='handler.test_list'),
#              ),
#         title='Test type information',
#         buttons=['OK'],
#         resizable = True,
#         handler=TestHandler
#     )
#     # test_type = Enum()
#     def list_output(self):
#         return self.CT_list
#
#
# class TestHandler(Handler):
#     """
#     Handler class to redefine the possible values of 'city' based on 'state'.
#     This handler will be assigned to a view of an Address, and can listen and
#     respond to changes in the viewed Address.
#     """
#
#     # Current list of available cities:
#     test_list = tr.List(tr.Str)
#
#     def object_test_type_changed(self, info):
#         """
#         This method listens for a change in the *state* attribute of the
#         object (Address) being viewed.
#         When this listener method is called, *info.object* is a reference to
#         the viewed object (Address).
#         """
#         # Change the list of available cities
#         self.tests = tests[info.object.test_type]
#
#         # As default value, use the first city in the list:
#         info.object.test = self.tests[0]
