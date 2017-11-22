__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 17, 2017'
__status__ = 'Draft'

from traits.api import \
    HasStrictTraits, HasTraits, Int, Str, Float, Array, Property, cached_property
from traitsui.api import View, Item, Group
import traitsui
import pandas as pd
import numpy as np


# --------------------------------------------------------------------------
# definition of classes for the different experiment types and the materials
# --------------------------------------------------------------------------


class BeamEndTest (HasStrictTraits):

    height = Float(unit='mm')

    length = Float(unit='mm')

    width = Float(unit='mm')

    bond_length = Float(unit='mm')

    number_longitudinal_ri = Int (1)

    number_stirrup = Int (1)

    traits_view = View(Group(Item(name = 'height'),
                             Item(name='length'),
                             Item(name='width'),
                             Item(name='bond_length'),
                             Item(name='number_longitudinal_ri'),
                             Item(name='number_stirrup'),
                             label = 'Beam End', show_border = True))


class Reinforcement(HasStrictTraits):

    diameter_long_ri = Int(unit='mm')

    diameter_stirrup = Int(unit='mm')

    material_long_ri = Str('Steel')

    material_stirrup = Str('Steel')

    category_long_ri = Str('B500')

    category_stirrup = Str('B500')

    strength_long_ri = Float(unit='MPa')

    strength_stirrup = Float(unit='MPa')


class Concrete(HasStrictTraits):

    category_c = Str('C120')

    strength_c = Float(unit='MPa')

    date_production = pd.to_datetime('2017-10-01')

    date_test = pd.to_datetime('2017-11-01')

    age_specimen = Int(unit='d')


class CylinderTest(HasStrictTraits):

    #-----------------------------------------------
    # input variables
    # ----------------------------------------------

    data = Array(np.float_, input=True)

    height = Float(300.0, unit='mm')

    diameter = Float(100.0, unit='mm')

    category_c = Str('C120')

    strength_c = Float(120.0, unit='MPa')

    date_production = pd.to_datetime('2017-10-01')

    date_test = pd.to_datetime('2017-11-01')

    age_specimen = Float(56.0, unit='d')

    loading_scenario = Str('LS1')

    frequency = Float(5.0, unit='Hz')

    loading_cycles = Str(100)

    # -----------------------------------------------
    # property / cached_property
    # -----------------------------------------------

    argmax_force = Property(depends_on='+input')

    # index of maximum force f_max
    @cached_property
    def _get_argmax_force(self):
        f = data[:, 1]
        return np.argmin(f)

    t = Property(depends_on='+input')

    # time at f_max
    @cached_property
    def _get_t(self):
        return self.data[:self.argmax_force, 0]

    f = Property(depends_on='+input')

    # maximum force f_max
    @cached_property
    def _get_f(self):
        return -self.data[:self.argmax_force, 1]

    u = Property(depends_on='+input')

    # machine displacement at f_max
    @cached_property
    def _get_u(self):
        return -self.data[:self.argmax_force, 2]

    wa1 = Property(depends_on='+input')

    # gauge 1 displacement at f_max
    @cached_property
    def _get_wa1(self):
        return self.data[:self.argmax_force, 3]

    wa2 = Property(depends_on='+input')

    # gauge 2 displacement at f_max
    @cached_property
    def _get_wa2(self):
        return self.data[:self.argmax_force, 4]

    wa3 = Property(depends_on='+input')

    # gauge 3 displacement at f_max
    @cached_property
    def _get_wa3(self):
        return self.data[:self.argmax_force, 5]


if __name__ == '__main__':

    be = BeamEndTest()

    be.height = 100

    be.configure_traits()




