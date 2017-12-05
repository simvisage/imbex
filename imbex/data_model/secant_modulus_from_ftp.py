__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Dec. 5, 2017'
__status__ = 'Active'


# imports
import numpy as np
import pandas as pd
import pylab as p
import os
from experiment_types import CylinderTest, SFTPConnection, RequestedTest


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
    # this was planned to reduce the read data by excluding columns
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

    # dictionary defining basic layout of plots
    params = {'legend.fontsize': 'large',
              'figure.figsize': (15, 5),
              'axes.labelsize': 'large',
              'axes.titlesize': 'medium',
              'xtick.labelsize': 'medium',
              'ytick.labelsize': 'medium',
              'lines.linewidth': 1,
              'axes.linewidth': 1,
              'lines.markersize': 4}

    # applies design from params dictionary to pylab
    p.rcParams.update(params)

    # defines numbers and positions of subplots
    ax1 = p.subplot(3, 1, 1)
    ax2 = p.subplot(3, 1, 3)
    ax3 = p.subplot(3, 1, 2)

    # 'index distance' to neighbour for calculation of difference
    delta_arg2 = 20

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

    # shapes of up/down args are also the number of cycles
    print(up_args.shape)
    print(down_args.shape)

    # cross-section of cylinder tests [mm**2]
    A_ct = np.pi*50**2

    # height of cylinder tests [mm]
    h_ct = 300

    # calculates the stress from the force
    sig_up = -(ct.f[up_args]*10**3)/A_ct
    sig_down = -(ct.f[down_args]*10**3)/A_ct
    sig_m = (sig_up+sig_down)/2

    # calculates the strain from gauge wa1
    eps_wa1_up = ct.wa1[up_args]/h_ct
    eps_wa1_down = ct.wa1[down_args]/h_ct

    # scales the min/max stress to mean stress
    sig_up_scale = sig_up/sig_m
    sig_down_scale = sig_down

    rig = (sig_up_scale-sig_down_scale)/(eps_wa1_up-eps_wa1_down)
    cycles = np.arange(np.ma.size(up_args))

    ax1.set_xlabel('time [s]')
    ax1.set_ylabel('force [kN]')
    ax1.plot(ct.t, ct.f)
    ax1.plot(ct.t[up_args], ct.f[up_args], 'go')
    ax1.plot(ct.t[down_args], ct.f[down_args], 'go')

    ax2.set_xlabel('cycles')
    ax2.set_ylabel('rigidity [MPa]')
    ax2.plot(cycles, rig, 'ro')
    ax2.plot(cycles, rig)

    ax3.set_xlabel('time [s]')
    ax3.set_ylabel('force [kN]')
    ax3.plot(ct.wa1, ct.f)
    ax3.plot(ct.wa1[up_args], ct.f[up_args], 'go')
    ax3.plot(ct.wa1[down_args], ct.f[down_args], 'go')

    p.show()
