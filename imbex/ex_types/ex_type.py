__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 10, 2017'
__status__ = 'Draft'

from traits.api import \
    HasStrictTraits, Int, Str, Float
import pandas as pd


class SpecimenDimensions(HasStrictTraits):

    height = Float(unit='mm')

    length = Float(unit='mm')

    width = Float(unit='mm')

    diameter = Float(unit='mm')

    bond_length = Float(unit='mm')

    number_long_ri = Int

    number_stirrup = Int


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

    category_c = Str('B500')

    strength_c = Float(unit='MPa')

    date_production = pd.to_datetime('2017-10-01')

    date_test = pd.to_datetime('2017-11-01')

    age_specimen = Int(unit='d')


if __name__ == '__main__':
    r = Reinforcement()

    r.rho = 24.6

    r.configure_traits()
