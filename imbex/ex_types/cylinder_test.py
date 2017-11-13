__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 10, 2017'
__status__ = 'Draft'

import numpy as np
from traits.api import\
    HasTraits, Float, Str, Int, Array, Property, cached_property
import pandas as pd
import os
import pylab as p

# ---------------------------------------------------------------
# definition of class for cylinder tests
# ---------------------------------------------------------------


class cylinder_test (HasTraits):

        #-----------------------------------------------
        # input variables
        # ----------------------------------------------

        # data = Array(np.float_, input=True)

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

if __name__ == '__main__':

    # name of the current test
    test = 'CT_120_1_6'

    # directory of raw data
    raw_data_dir=os.path.join('/users/macretina/sciebo/imb/python', 'rawdata_CT', '%s.csv' %(test))

    # function to change the decimal from ',' to '.'
    def decimal_comma (value):
            value = value.replace(',','.')
            return float(value)

    # loads the *.csv file
    data = np.loadtxt(raw_data_dir, dtype=np.float, skiprows=2, converters={0: decimal_comma, 1: decimal_comma, 2: decimal_comma, 3: decimal_comma, 4: decimal_comma,5: decimal_comma}, delimiter=';')

    # defines ct as instance of the class cylinder_test
    ct = cylinder_test(data=data)

    # definition of positions od subplots
    ax1 = p.subplot(3, 2, 1)
    ax2 = p.subplot(3, 2, 2)
    ax3 = p.subplot(3, 2, 3)
    ax4 = p.subplot(3, 2, 4)
    ax5 = p.subplot(3, 2, 5)
    ax6 = p.subplot(3, 2, 6)

    # definition of the charts
    ax1.plot(ct.t, ct.f)
    ax2.plot(ct.wa1, ct.f)
    ax2.plot(ct.wa2, ct.f)
    ax2.plot(ct.wa3, ct.f)

    delta_arg2 =20

    # derivatives df and ddf
    df = ct.f[2*delta_arg2:]-ct.f[:-2*delta_arg2]
    ddf = df[2*delta_arg2:]-df[:-2*delta_arg2]

    ax3.plot(ct.t[delta_arg2:-delta_arg2], df)
    ax4.plot(ct.t[2*delta_arg2:-2*delta_arg2],ddf)

    df_threshold = 0.0
    ddf_threshold = 0.0
    Df = df[delta_arg2:-delta_arg2]
    # print ct.f.shape
    # print Df.shape
    # print ddf.shape

    up_args_dd = np.where(((Df[1:]*Df[:-1]<df_threshold)*((ddf[1:]+ddf[:-1])/2.0<ddf_threshold)))[0]

    up_args_d = up_args_dd + delta_arg2

    up_args = up_args_d + delta_arg2

    ax1.plot(ct.t[up_args], ct.f[up_args], 'go')
    ax3.plot(ct.t[delta_arg2:-delta_arg2][up_args_d],df[up_args_d], 'go')
    ax4.plot(ct.t[up_args], ddf[up_args_dd], 'go')

    down_args_dd = np.where(((Df[1:] * Df[:-1] < df_threshold) * ((ddf[1:] + ddf[:-1]) / 2.0 > ddf_threshold)))[0]

    down_args_d = down_args_dd + delta_arg2

    down_args = down_args_d + delta_arg2

    ax1.plot(ct.t[down_args], ct.f[down_args], 'go')
    ax3.plot(ct.t[delta_arg2:-delta_arg2][down_args_d], df[down_args_d], 'go')
    ax4.plot(ct.t[down_args], ddf[down_args_dd], 'go')

    f_envelope_up = np.hstack([ct.f[:up_args[0]], ct.f[up_args[1:]]])
    u_envelope_up = np.hstack([ct.u[:up_args[0]], ct.u[up_args[1:]]])

    f_envelope_down = np.hstack([ct.f[:down_args[0]], ct.f[down_args[1:]]])
    u_envelope_down = np.hstack([ct.u[:down_args[0]], ct.u[down_args[1:]]])


    ax5.plot(u_envelope_up, f_envelope_up)
    ax5.plot(u_envelope_down, f_envelope_down)

    selected_cycles = np.array([1, 20, 40], dtype=np.int_)

    selected_cycles_start_args = up_args[selected_cycles]
    selected_cycles_end_args = up_args[selected_cycles +1]

    for sc in selected_cycles:
        s_arg = up_args[sc]
        e_arg = up_args[sc+1]
        ax6.plot(ct.u[s_arg:e_arg], ct.f[s_arg:e_arg],)


    p.show()

