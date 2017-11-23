__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 23, 2017'
__status__ = 'Final'


import paramiko
import pandas as pd
import os



# class for SFTP connection using paramiko
class SFTPConnection:

    # returns a SFTP-Connection with given arguments
    def __init__(self, test, username, password):
        self.test = test
        self.username = username
        self.password = password
        self.host = "134.130.81.25"
        self.port = 22

    # returns the path of the local file after downloading it from the server
    def connection(self):
        transport = paramiko.Transport(self.host, self.port)
        transport.connect(username=self.username, password=self.password)
        sftp = paramiko.SFTPClient.from_transport(transport)
        filepath = '/home/ftp/austausch_chudoba/raw_data/%s.csv' % test
        localpath = './%s.csv' % test
        sftp.get(filepath, localpath)
        return localpath

#name of the considered test
test = 'CT_120_1_6'
# username and password for authentication
username = "ftp"
password = "!mb1@FTP7"

# calls the class for a SFTP-connection
RA = SFTPConnection(test, username, password)

# reads the downloaded .csv file using pandas
data = pd.read_csv(RA.connection(), sep=';', decimal=',', skiprows=2, nrows=5)

print(data)

# deletes the local file
os.remove(RA.connection())

