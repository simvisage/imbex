__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 23, 2017'
__status__ = 'Final'


import paramiko
import pandas as pd
from traits.api import *
from traitsui.api import*
import os



# class for SFTP connection using paramiko
class SFTPConnection(HasTraits):

    username = Str(desc="username",
        label="username", )

    password = Str(desc="password",
        label="password", )

    traits_view = View(Group(Item(name = 'username'),
                             Item(name = 'password'),
                             label = 'authentication',
                             show_border = True))

    def output(self):
        print('Login as user "%s" with password "%s".' %(
                self.username, self.password))

    # returns a SFTP-Connection with given arguments
    def __init__(self, test, filepath, localpath):
        self.test = test
        self.host = "134.130.81.25"
        self.port = 22
        self.filepath = filepath
        self.localpath = localpath

    # returns the path of the local file after downloading it from the server
    def connect(self):
        global sftp
        global transport
        transport = paramiko.Transport(self.host, self.port)
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        sftp.get(self.filepath, self.localpath)
        return self.localpath

    def disconnect (self):
        return [sftp.close(), transport.close()]


if __name__ == '__main__':
    test = 'CT_120_1_6'
    filepath = '/home/ftp/austausch_chudoba/raw_data/%s.csv' %test
    localpath = './%s.csv' %test
    # calls the class for a SFTP-connection
    RA = SFTPConnection(test, filepath, localpath)

    RA.configure_traits()

    RA.output()

    #name of the considered test


    # reads the downloaded .csv file using pandas
    data = pd.read_csv(RA.connect(), sep=';', decimal=',', skiprows=None, nrows=5)

    print(data)

    # disconnects from sftp and deletes the local file
    RA.disconnect()



