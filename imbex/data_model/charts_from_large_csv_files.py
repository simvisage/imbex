__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Dec. 05, 2017'
__status__ = 'Rejected'

import numpy as np
from traits.api import\
    HasStrictTraits, Float, Str, Int, Array, Property, cached_property
import pandas as pd
import os
import pylab as p

# ---------------------------------------------------------------
# class definition for cylinder tests
# ---------------------------------------------------------------


class CylinderTest (HasStrictTraits):

        #-----------------------------------------------
        # input variables
        # ----------------------------------------------

        data = Array(np.float_, input=True)

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
                return -self.data[:self.argmax_force, 5]

        wa1 = Property(depends_on='+input')

        # gauge 1 displacement at f_max
        @cached_property
        def _get_wa1(self):
                return self.data[:self.argmax_force, 2]

        wa2 = Property(depends_on='+input')

        # gauge 2 displacement at f_max
        @cached_property
        def _get_wa2(self):
                return self.data[:self.argmax_force, 3]

        wa3 = Property(depends_on='+input')

        # gauge 3 displacement at f_max
        @cached_property
        def _get_wa3(self):
                return self.data[:self.argmax_force, 4]

if __name__ == '__main__':

    test = 'CT_120_1_8'

    data = os.path.join('/users/macretina/sciebo/imb/python', 'rawdata_CT', '%s.csv' % (test))

    names=['Zeit [s]', 'Kraft [kN]', 'Maschinenweg [mm]', 'WA_1 [mm]', 'WA_2 [mm]', 'WA_3 [mm]']

    F=names[1]
    WA_1 = names[3]
    WA_2 = names[4]
    WA_3 = names[5]

    columns_to_keep = [0,1,3,4,5]

    data2 = pd.read_csv(data, sep=';', decimal=',', skiprows=2, nrows=None, usecols=columns_to_keep)

    data1= data2.as_matrix(columns=None)
    data = data1[::]

    # defines ct as instance of the class cylinder_test
    ct = CylinderTest(data=data)

    # definition of positions od subplots
    # ax1 = p.subplot(1, 1, 1)
    ax1 = p.subplot(2, 3, 1)
    ax2 = p.subplot(2, 3, 2)
    ax3 = p.subplot(2, 3, 4)
    ax4 = p.subplot(2, 3, 5)
    ax5 = p.subplot(2, 3, 3)
    ax6 = p.subplot(2, 3, 6)

    ax1.plot(ct.t, ct.f)
    ax3.plot(ct.t, ct.wa1, 'g')
    ax3.plot(ct.t, ct.wa2, 'r')
    ax3.plot(ct.t, ct.wa3, 'b')

    delta_arg2 = 1

    df = ct.f[2 * delta_arg2:] - ct.f[:-2 * delta_arg2]
    ddf = df[2 * delta_arg2:] - df[:-2 * delta_arg2]

    print df.shape

    dt_t = ct.t[2 * delta_arg2:-2 * delta_arg2]

    ax2.plot(ct.t[delta_arg2:-delta_arg2], df)
    ax5.plot(ct.t[2*delta_arg2:-2*delta_arg2], ddf)

    df_threshold = 0.0
    ddf_threshold = 0.0
    Df = df[delta_arg2:-delta_arg2]

    up_args_dd = np.where(
        ((Df[1:] * Df[:-1] < df_threshold)) * ((ddf[1:] + ddf[:-1]) / 2.0 < ddf_threshold))[0]

    up_args_d = up_args_dd + delta_arg2

    up_args = up_args_d + delta_arg2

    down_args_dd = np.where(
        ((Df[1:] * Df[:-1] < df_threshold) * ((ddf[1:] + ddf[:-1]) / 2.0 > ddf_threshold)))[0]

    down_args_d = down_args_dd + delta_arg2

    down_args = down_args_d + delta_arg2

    ax1.plot(ct.t[up_args], ct.f[up_args], 'go')

    ax1.plot(ct.t[down_args], ct.f[down_args], 'go')

    t_envelope_up = np.hstack([ct.t[:up_args[0]], ct.t[up_args[1:]]])
    wa1_envelope_up = np.hstack([ct.wa1[:up_args[0]], ct.wa1[up_args[1:]]])
    wa2_envelope_up = np.hstack([ct.wa2[:up_args[0]], ct.wa2[up_args[1:]]])
    wa3_envelope_up = np.hstack([ct.wa3[:up_args[0]], ct.wa3[up_args[1:]]])


    t_envelope_down = np.hstack([ct.t[:down_args[0]], ct.t[down_args[1:]]])
    wa1_envelope_down = np.hstack([ct.wa1[:down_args[0]], ct.wa1[down_args[1:]]])
    wa2_envelope_down = np.hstack([ct.wa2[:down_args[0]], ct.wa2[down_args[1:]]])
    wa3_envelope_down = np.hstack([ct.wa3[:down_args[0]], ct.wa3[down_args[1:]]])


    ax4.plot(t_envelope_up, wa1_envelope_up, 'g')
    ax4.plot(t_envelope_up, wa2_envelope_up, 'r')
    ax4.plot(t_envelope_up, wa3_envelope_up, 'b')

    wa_env_avg_up = (wa1_envelope_up+wa2_envelope_up+wa3_envelope_up)/3
    wa_env_avg_down = (wa1_envelope_down+wa2_envelope_down+wa3_envelope_down)/3

    ax4.plot(t_envelope_down, wa1_envelope_down, 'g')
    ax4.plot(t_envelope_down, wa2_envelope_down, 'r')
    ax4.plot(t_envelope_down, wa3_envelope_down, 'b')
    ax4.plot(t_envelope_up, wa_env_avg_up, '0.5')
    ax4.plot(t_envelope_down, wa_env_avg_down, '0.5')

    ax6.plot(t_envelope_up, wa_env_avg_up, '0.5')
    ax6.plot(t_envelope_down, wa_env_avg_down, '0.5')

    p.show()
