__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 10, 2017'
__status__ = 'Draft'

import numpy as np
from traits.api import\
    HasStrictTraits, Float, Str, Int, Array, Property, cached_property
import pandas as pd
import os
import pylab as p

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


# ---------------------------------------------------------------
# script to analyse the data
# ---------------------------------------------------------------


test = 'CT_120_1_13'
# directory of raw data
raw_data_dir=os.path.join('/users/macretina/sciebo/imb/python', 'rawdata_CT', '%s.csv' %(test))

def decimal_comma (value):
        value = value.replace(',','.')
        return float(value)

data = np.loadtxt(raw_data_dir, dtype=np.float, skiprows=2, converters={0: decimal_comma, 1: decimal_comma, 2: decimal_comma, 3: decimal_comma, 4: decimal_comma,5: decimal_comma}, delimiter=';')

ct = cylinder_test(data=data)

ax1 = p.subplot(2,3,1)
ax2 = p.subplot(2,3,2)
ax3 = p.subplot(2,3,3)
ax4 = p.subplot(2,3,4)


ax1.plot(ct.t, ct.f)
ax2.plot(ct.u, ct.f)
ax2.plot(ct.wa1, ct.f)
ax2.plot(ct.wa2, ct.f)
ax2.plot(ct.wa3, ct.f)

p.show()

