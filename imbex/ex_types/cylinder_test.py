from imbex.ex_types.ex_type import SpecimenDimensions

__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 10, 2017'
__status__ = 'Draft'

# import section
from imbex.ex_types.ex_type import SpecimenDimensions, Reinforcement, Concrete
import numpy as np
from traits.api import\
    HasStrictTraits, Float, String, Int
import datetime as dat


class cylinder_test (SpecimenDimensions, Reinforcement, Concrete):

    def __init__(self, name, height):
        self.name = name
        self.height = 300

    def get_height(self):
        return self.height





ct = cylinder_test

print (ct.height)