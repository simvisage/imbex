__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 10, 2017'
__status__ = 'Draft'

import numpy as np
from traits.api import\
    HasStrictTraits, Float, Str, Int, Array, Property, cached_property
import pandas as pd

# ---------------------------------------------------------------
# definition of class for cylinder tests
# ---------------------------------------------------------------


class cylinder_test (HasStrictTraits):

        #-----------------------------------------------
        # input variables
        # ----------------------------------------------

        data = Array(np.float_, input=True      )

        height = Int(300, unit='mm')

        diameter = Int(100, unit='mm')

        category_c = Str('C120')

        strength_c = Float(120.0, unit='MPa')

        date_production = pd.to_datetime('2017-10-01')

        date_test = pd.to_datetime('2017-11-01')

        age_specimen = Int(56, unit='d')

        loading_scenario = Str('LS1')

        frequency = Int(5, unit='Hz')

        loading_cycles = Str(100)


        # -----------------------------------------------
        # property / cached_property
        # -----------------------------------------------


        argmax_force = Property(depends_on='+input')

        # index of maximum force f_max
        @cached_property
        def _get_argmax_force(self):
                f = data[:,1]
                return np.argmin(f)


        t = Property(depends_on='+input')

        # time at f_max
        @cached_property
        def _get_t(self):
                return self.data[:self.argmax_force,0]

        f = Property(depends_on='+input')

        # maximum force f_max
        @cached_property
        def _get_f(self):
                return -self.data[:self.argmax_force,1]

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
