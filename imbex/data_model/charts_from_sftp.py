__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 16, 2017'
__status__ = 'Draft'

import os

from experiment_types import CylinderTest, SFTPConnection, RequestedTest
import numpy as np
import pandas as pd
import pylab as p


if __name__ == '__main__':

    # name of the requested test
    rt = RequestedTest()

    rt.configure_traits()

    rt.check_test_name()

    filepath = '/home/ftp/austausch_chudoba/raw_data/%s.csv' % rt.output_test()
    localpath = './%s.csv' % rt.output_test()

    # SC: server connection is instance of class SFTPConnection
    sc = SFTPConnection(rt.output_test(), filepath, localpath)

    sc.configure_traits()

    sc.check_authentication()

    names = ['Zeit [s]', 'Kraft [kN]', 'Maschinenweg [mm]',
             'WA_1 [mm]', 'WA_2 [mm]', 'WA_3 [mm]']

    F = names[1]
    WA_1 = names[3]
    WA_2 = names[4]
    WA_3 = names[5]

    columns_to_keep = [0, 1, 2, 3, 4, 5]

    data2 = pd.read_csv(sc.connect(), sep=';', decimal=',',
                        skiprows=2, nrows=None, usecols=columns_to_keep)

    data1 = data2.as_matrix(columns=None)
    data0 = data1[::]

    # defines ct as instance of the class cylinder_test
    ct = CylinderTest(data=data0)

    # disconnects from sftp-server
    sc.disconnect()
    # deletes the local file
    os.remove(sc.connect())

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

    print (df.shape)

    dt_t = ct.t[2 * delta_arg2:-2 * delta_arg2]

    ax2.plot(ct.t[delta_arg2:-delta_arg2], df)
    ax5.plot(ct.t[2 * delta_arg2:-2 * delta_arg2], ddf)

    df_threshold = 0.0
    ddf_threshold = 0.0
    Df = df[delta_arg2:-delta_arg2]

    up_args_dd = np.where(
        (Df[1:] * Df[:-1] < df_threshold) * ((ddf[1:] + ddf[:-1]) / 2.0 < ddf_threshold))[0]

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
    wa1_envelope_down = np.hstack(
        [ct.wa1[:down_args[0]], ct.wa1[down_args[1:]]])
    wa2_envelope_down = np.hstack(
        [ct.wa2[:down_args[0]], ct.wa2[down_args[1:]]])
    wa3_envelope_down = np.hstack(
        [ct.wa3[:down_args[0]], ct.wa3[down_args[1:]]])

    ax4.plot(t_envelope_up, wa1_envelope_up, 'g')
    ax4.plot(t_envelope_up, wa2_envelope_up, 'r')
    ax4.plot(t_envelope_up, wa3_envelope_up, 'b')

    wa_env_avg_up = (wa1_envelope_up + wa2_envelope_up + wa3_envelope_up) / 3
    wa_env_avg_down = (wa1_envelope_down +
                       wa2_envelope_down + wa3_envelope_down) / 3

    ax4.plot(t_envelope_down, wa1_envelope_down, 'g')
    ax4.plot(t_envelope_down, wa2_envelope_down, 'r')
    ax4.plot(t_envelope_down, wa3_envelope_down, 'b')
    ax4.plot(t_envelope_up, wa_env_avg_up, '0.5')
    ax4.plot(t_envelope_down, wa_env_avg_down, '0.5')

    ax6.plot(t_envelope_up, wa_env_avg_up, '0.5')
    ax6.plot(t_envelope_down, wa_env_avg_down, '0.5')

    p.show()
