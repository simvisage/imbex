__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 24, 2017'
__status__ = 'Draft'

# Imports:
import os
from traits.api import HasTraits, Enum
from traitsui.api import Item, Group, View, EnumEditor


class TestTypEnum(HasTraits):
    test_typ_list = Enum('Beam-End-Tests', 'Cylinder-Tests', 'Stress-Redistribution-Tests')

    enum_group = Group(
        Item('test_typ_list', style='simple', label='Simple')
    )

    # Demo view:
    traits_view = View(
        enum_group,
        title='EnumEditor',
        buttons=['OK'],
        resizable=True
    )

    def output_test_typ (self):
        return self.test_typ_list


if __name__ == '__main__':
    tte = TestTypEnum()

    tte.configure_traits()

    print(tte.output_test_typ())

    directory = '/home/ftp/austausch_chudoba/%s/raw_data' % tte.output_test_typ()

    # SC: server connection is instance of class SFTPConnection
    sc = SFTPConnection(test, filepath, localpath)

    sc.configure_traits()

    sc.check_authentication()

    names = ['Zeit [s]', 'Kraft [kN]', 'Maschinenweg [mm]', 'WA_1 [mm]', 'WA_2 [mm]', 'WA_3 [mm]']

    F = names[1]
    WA_1 = names[3]
    WA_2 = names[4]
    WA_3 = names[5]

    columns_to_keep = [0, 1, 2, 3, 4, 5]

    data2 = pd.read_csv(sc.connect_file(), sep=';', decimal=',', skiprows=None, nrows=3, usecols=columns_to_keep)

    print(data2)

    # disconnects from sftp-server
    sc.disconnect()
    # deletes the local file
    os.remove(sc.connect())