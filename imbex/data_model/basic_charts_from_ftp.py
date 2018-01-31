__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Jan. 31, 2018'
__status__ = 'Active'


# imports
import numpy as np
import scipy as sp
import pandas as pd
import pylab as p
import os
from experiment_types import BeamEndTest, CylinderTest, SFTPConnection, RequestedTest
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

    # returns test type chosen by user from dialog box
    test_type = sc.output_test_type()

    #dictionary assigns class names to the requested test typ
    exp_classes = {'Cylinder-Tests':'CylinderTest', 'Beam-End-Tests':'BeamEndTest', 'Stress-Redistribution-Tests':'StressRedistributionTest'}

    # returns the class assigned from the dictionary exp_classes by chosen test type
    requested_exp_class = exp_classes[sc.output_test_type()]

    # sets the class name (e.g. CylinderTest) as global variable
    exp_type_class = globals()[requested_exp_class]

    # test type chosen by user from drop-down dialog box
    test = rt.output_test()

    names = ['Zeit [s]', 'Kraft [kN]', 'Maschinenweg [mm]', 'WA_1 [mm]', 'WA_2 [mm]', 'WA_3 [mm]', 'WA_4 [mm]']

    F = names[1]
    WA_1 = names[3]
    WA_2 = names[4]
    WA_3 = names[5]
    WA_4 = names[6]

    # Caution: modification of this list have also be done in Cylinder-Test class
    # this was planned to reduce read data by excluding columns
    # columns_to_keep = [0, 1, 2, 3, 4, 5]


    # raw data is read using pandas and returned as DataFrame
    dataframe = pd.read_csv(sc.transport_file(test_type, test), sep=';', decimal=',', skiprows=2, nrows=None, usecols=None)

    # converts DataFrame to Numpy array
    data = dataframe.as_matrix(columns=None)

    # defines exp_1 as instance of the class cylinder_test
    exp_1 = exp_type_class(data=data)

    # disconnects from sftp-server
    sc.disconnect()

    # deletes the local file
    os.remove(sc.local_raw_file())

    delta_arg2 = 1

    df = exp_1.f[2 * delta_arg2:] - exp_1.f[:-2 * delta_arg2]
    ddf = df[2 * delta_arg2:] - df[:-2 * delta_arg2]

    print ('Shape of df = %s' %df.shape)

    dt_t = exp_1.t[2 * delta_arg2:-2 * delta_arg2]

    df_threshold = 0.0
    ddf_threshold = 0.0
    Df = df[delta_arg2:-delta_arg2]

    up_args_dd = np.where(
        (Df[1:] * Df[:-1] < df_threshold) * ((ddf[1:] + ddf[:-1]) / 2.0 < ddf_threshold))[0]

    up_args_d = up_args_dd + delta_arg2

    up_args = up_args_d + delta_arg2

    print(type(up_args))

    down_args_dd = np.where(
        ((Df[1:] * Df[:-1] < df_threshold) * ((ddf[1:] + ddf[:-1]) / 2.0 > ddf_threshold)))[0]

    down_args_d = down_args_dd + delta_arg2

    down_args = down_args_d + delta_arg2

    t_envelope_up = np.hstack([exp_1.t[:up_args[0]], exp_1.t[up_args[1:]]])
    wa1_envelope_up = np.hstack([exp_1.wa1[:up_args[0]], exp_1.wa1[up_args[1:]]])
    wa2_envelope_up = np.hstack([exp_1.wa2[:up_args[0]], exp_1.wa2[up_args[1:]]])
    wa3_envelope_up = np.hstack([exp_1.wa3[:up_args[0]], exp_1.wa3[up_args[1:]]])

    t_envelope_down = np.hstack([exp_1.t[:down_args[0]], exp_1.t[down_args[1:]]])
    wa1_envelope_down = np.hstack([exp_1.wa1[:down_args[0]], exp_1.wa1[down_args[1:]]])
    wa2_envelope_down = np.hstack([exp_1.wa2[:down_args[0]], exp_1.wa2[down_args[1:]]])
    wa3_envelope_down = np.hstack([exp_1.wa3[:down_args[0]], exp_1.wa3[down_args[1:]]])


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
    ax1.plot(exp_1.t, exp_1.f)
    ax1.plot(exp_1.t, exp_1.wa1)
    ax1.plot(exp_1.t, exp_1.wa2)
    ax1.plot(exp_1.t, exp_1.wa3)

    ax1.plot(exp_1.t[up_args], exp_1.f[up_args], 'go')
    ax1.plot(exp_1.t[down_args], exp_1.f[down_args], 'go')

    ax2.set_xlabel('x-axis')
    ax2.set_ylabel('y-axis')
    ax2.plot(exp_1.t[delta_arg2:-delta_arg2], df)

    ax3.set_xlabel('time')
    ax3.set_ylabel('displacement')
    ax3.plot(exp_1.t, exp_1.wa1, 'g')
    ax3.plot(exp_1.t, exp_1.wa2, 'r')
    ax3.plot(exp_1.t, exp_1.wa3, 'b')

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
    ax5.plot(exp_1.wa1[up_args], exp_1.f[up_args], 'go')
    ax5.plot(exp_1.wa1[down_args], exp_1.f[down_args], 'go')
    # ax5.plot(exp_1.t[2*delta_arg2:-2*delta_arg2], ddf)
    ax5.plot(exp_1.wa1, exp_1.f)

    ax6.set_xlabel('time')
    ax6.set_ylabel('displacement')
    ax6.plot(t_envelope_up, wa_env_avg_up, '0.5')
    ax6.plot(t_envelope_down, wa_env_avg_down, '0.5')

    # ax6.set_xlabel('force')
    # ax6.set_ylabel('displacement')
    # ax6.plot(exp_1.wa1, exp_1.f, 'g')
    # ax6.plot(exp_1.wa2, exp_1.f, 'r')
    # ax6.plot(exp_1.wa3, exp_1.f, 'b')

    p.show()














