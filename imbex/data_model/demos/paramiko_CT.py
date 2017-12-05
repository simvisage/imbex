__author__ = 'campsb'
__copyright = 'Copyright 2009, IMB, RWTH Aachen'
__date__ = 'Nov. 23, 2017'
__status__ = 'Final'




import paramiko
import pandas as pd
import os


test = 'CT_120_1_6'

# open a transport
host = "134.130.81.25"
port = 22
transport = paramiko.Transport((host, port))

# auth
username = input ('Enter your username')
password = input('Enter your password.')
transport.connect(username = username, password = password)
sftp = paramiko.SFTPClient.from_transport(transport)

# Download
filepath = '/home/ftp/austausch_chudoba/raw_data/%s.csv' %test
localpath = './%s.csv' %test
sftp.get(filepath, localpath)

# path = ServerAccess
data = pd.read_csv(localpath, sep=';', decimal=',', skiprows=2, nrows=5)

print(data)
# Close
sftp.close()
transport.close()
os.remove(localpath)