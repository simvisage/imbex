__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Dec. 5, 2017'
__status__ = 'Active'


# imports
import numpy as np
import scipy as sp
import pandas as pd
import pylab as p
import os
from experiment_types import CylinderTest, SFTPConnection, RequestedTest
from chart_types import BasicLayout


if __name__ == '__main__':

    # sc = server connection instances connects to ftp server defined in class SFTPConnection
    sc = SFTPConnection()
    sc.configure_traits(view='traits_view')
    sc.configure_traits(view='traits_view2')
    sc.check_inputs()

    # directory with files to be listed in the drop-down list
    directory = sc.requested_directory()

    # list of files in the requested directory
    file_list1 = sc.list_files(directory)

    # rt = instance to generate the drop-down list
    rt = RequestedTest(file_list=sc.list_files(directory))
    rt.configure_traits()
    rt.check_input()

    # test type chosen be user from first dialog box
    test_type = sc.output_test_type()

    # test type chosen be user from drop-down dialog box
    test = rt.output_test()

    names = ['Zeit [s]', 'Kraft [kN]', 'Maschinenweg [mm]', 'WA_1 [mm]', 'WA_2 [mm]', 'WA_3 [mm]']

    F = names[1]
    WA_1 = names[3]
    WA_2 = names[4]
    WA_3 = names[5]

    # Caution: modification of this list have also be done in Cylinder-Test class
    # this was planned to reduce read data by excluding columns
    columns_to_keep = [0, 1, 2, 3, 4, 5]

    # raw data is read using pandas and returned as DataFrame
    dataframe = pd.read_csv(sc.transport_file(test_type, test), sep=';', decimal=',', skiprows=100, nrows=None, usecols=columns_to_keep)

    # converts DataFrame to Numpy array
    data = dataframe.as_matrix(columns=None)

    # defines ct as instance of the class cylinder_test
    ct = CylinderTest(data=data)

    # disconnects from sftp-server
    sc.disconnect()

    # deletes the local file
    os.remove(sc.local_raw_file())

    delta_arg2 = 1

    df = ct.f[2 * delta_arg2:] - ct.f[:-2 * delta_arg2]
    ddf = df[2 * delta_arg2:] - df[:-2 * delta_arg2]

    print (df.shape)

    dt_t = ct.t[2 * delta_arg2:-2 * delta_arg2]


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

    t_envelope_up = np.hstack([ct.t[:up_args[0]], ct.t[up_args[1:]]])
    wa1_envelope_up = np.hstack([ct.wa1[:up_args[0]], ct.wa1[up_args[1:]]])
    wa2_envelope_up = np.hstack([ct.wa2[:up_args[0]], ct.wa2[up_args[1:]]])
    wa3_envelope_up = np.hstack([ct.wa3[:up_args[0]], ct.wa3[up_args[1:]]])

    t_envelope_down = np.hstack([ct.t[:down_args[0]], ct.t[down_args[1:]]])
    wa1_envelope_down = np.hstack([ct.wa1[:down_args[0]], ct.wa1[down_args[1:]]])
    wa2_envelope_down = np.hstack([ct.wa2[:down_args[0]], ct.wa2[down_args[1:]]])
    wa3_envelope_down = np.hstack([ct.wa3[:down_args[0]], ct.wa3[down_args[1:]]])


    wa_env_avg_up = (wa1_envelope_up+wa2_envelope_up+wa3_envelope_up)/3
    wa_env_avg_down = (wa1_envelope_down+wa2_envelope_down+wa3_envelope_down)/3

    # applies the basic layout to the generated charts
    bl = BasicLayout()
    bl.apply_design()

    # defines positions of subplots
    # ax1 = p.subplot(1, 1, 1)
    ax1 = p.subplot(2, 3, 1)
    ax2 = p.subplot(2, 3, 2)
    ax3 = p.subplot(2, 3, 4)
    ax4 = p.subplot(2, 3, 5)
    ax5 = p.subplot(2, 3, 3)
    ax6 = p.subplot(2, 3, 6)

    ax1.set_xlabel('time')
    ax1.set_ylabel('force')
    ax1.plot(ct.t, ct.f)
    ax1.plot(ct.t[up_args], ct.f[up_args], 'go')
    ax1.plot(ct.t[down_args], ct.f[down_args], 'go')

    ax2.set_xlabel('x-axis')
    ax2.set_ylabel('y-axis')
    ax2.plot(ct.t[delta_arg2:-delta_arg2], df)

    ax3.set_xlabel('time')
    ax3.set_ylabel('displacement')
    ax3.plot(ct.t, ct.wa1, 'g')
    ax3.plot(ct.t, ct.wa2, 'r')
    ax3.plot(ct.t, ct.wa3, 'b')

    ax4.set_xlabel('time')
    ax4.set_ylabel('displacement')
    ax4.plot(t_envelope_down, wa1_envelope_down, 'g')
    ax4.plot(t_envelope_down, wa2_envelope_down, 'r')
    ax4.plot(t_envelope_down, wa3_envelope_down, 'b')
    ax4.plot(t_envelope_up, wa_env_avg_up, '0.5')
    ax4.plot(t_envelope_down, wa_env_avg_down, '0.5')
    ax4.plot(t_envelope_up, wa3_envelope_up, 'b')
    ax4.plot(t_envelope_up, wa1_envelope_up, 'g')
    ax4.plot(t_envelope_up, wa2_envelope_up, 'r')

    ax5.set_xlabel('time')
    ax5.set_ylabel('displacement')
    ax5.plot(ct.wa1[up_args], ct.f[up_args], 'go')
    ax5.plot(ct.wa1[down_args], ct.f[down_args], 'go')
    # ax5.plot(ct.t[2*delta_arg2:-2*delta_arg2], ddf)
    ax5.plot(ct.wa1, ct.f)

    ax6.set_xlabel('time')
    ax6.set_ylabel('displacement')
    ax6.plot(t_envelope_up, wa_env_avg_up, '0.5')
    ax6.plot(t_envelope_down, wa_env_avg_down, '0.5')

    p.show()














