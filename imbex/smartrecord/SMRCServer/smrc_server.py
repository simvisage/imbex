'''
Created on 05.05.2017

@author: mkennert
'''
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath('smrc_server.py'))))
from threading import Thread
import multiprocessing
import socket
import logging

class RunThread(Thread):
    """Thread which start automatically and has the daemon-mode"""

    def __init__(self, *args, **kw):
        super(RunThread, self).__init__(*args, **kw)
        self.daemon = True
        self.start()

class SMRC_Server(object):

    # The host will use if the configuration file of the server
    # does not exists.
    host = '134.130.81.25'

    # The port will use if the configuration file of the server
    # does not exists.
    port = 20000

    def __init__(self, *args, **kwargs):
        self.logger = self._create_logger('SMRC_Server')
        self.logger.info("""SMRC_Server with following properties was created:
        \t - host: {0}
        \t - port: {1}""".format(self.host, self.port))

    def start(self):
        """
        Creates a socket and connects it. After the connection the server 
        will wait for incoming connection and handle them. 
        """
        try:
            self.logger.debug('Try to create a socket and bind it')
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((self.host, self.port))
            self.logger.debug('Successfully binded.')
            self.socket.listen(5)
            self.logger.info('Listening for clients')
            while True:
                conn, address = self.socket.accept()
                self.logger.debug('Got connection')
                process = RunThread(target=self.handle, args=(conn, address))
                self.logger.debug('Started process %r', process)
        except:
            self.logger.exception('Unexpected exception')
        finally:
            self.logger.debug('Shutting down')
            for process in multiprocessing.active_children():
                self.logger.info('Shutting down process %r', process)
                process.terminate()
                process.join()
            self.logger.debug('All done')
            self.socket.close()
            sys.exit()

    def close(self):
        """
        Close all clients and the server. If the method was called
        the program will exit.
        """
        self.enable_clients = False
        self.enable_running = False
        # stop socket must be create to stop the accept-command of
        # in the start-method
        stop_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        stop_socket.connect((self.host, self.port))

    def handle(self, connection, address):
        """Create a ClientHandler and handle the connection with the socket

        :param connection: Address of the socket and the port
        :type connection: socket._socketobject  
        :param address: socket._socketobject 
        :type address: socket._socketobject 
        """
        logging.basicConfig(level=logging.DEBUG)
        logger = self._create_logger('process-' + str(address))
        handler = ClientHandler(self, connection)
        try:
            logger.debug('Connected %r at %r', connection, address)
            while True:
                try:
                    cmd = connection.recv(self.buffer_size)
                    if cmd == 'exit client':
                        logger.debug('Socket closed remotely')
                        break
                    elif len(cmd) > 0:
                        logger.debug('Received data %r', cmd)
                        logger.debug(handler.execute(cmd))
                except:
                    break
        except:
            logger.exception('Problem handling request')
        finally:
            logger.debug('Closing socket')
            connection.close()

    def _create_logger(self, name):
        # creates a logger to log all actions of the server.
        # name must be the name of the logger
        logging.basicConfig(level=logging.DEBUG)
        log_file = '../server.log'
        with open(log_file, 'w') as f:
            f.write('#Log all operations of the server\n')
        f.close()
        fmtr = logging.Formatter(fmt='%(asctime)s %(levelname)-8s %(message)s',
                                 datefmt='%Y-%m-%d %H:%M:%S')
        handler = logging.FileHandler(log_file, mode='a')
        handler.setFormatter(fmtr)
        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.addHandler(handler)
        return logger

import commands as cmd


class ClientHandler(object):
    """Class which handles the interaction with the server and the clients"""

    # smrc -cmd=command -args=arguments

    def __init__(self, model, connection):
        self.model = model
        self.connection = connection
        self.server_running = ""

    def _interpret_command(self, command):
        """Interpret the command and returns the related method with the arguments

        :param command: SMRC-Command
        :type command: string
        :returns: Returns the method and the arguments for the method
        :rtype: method, string
        :raises: ValueError
        """
        command, data = command.split('-data')
        method = command.split('=')[1].strip()
        args = data.split('=')[1].strip()
        return method, args

    def execute(self, command):
        """Interpret and execute the command.

        :param command: 
        :type command: string
        :returns: Information whether the execute was successful.
        :rtype: string
        """
        try:
            method, args = self._interpret_command(command)
            return getattr(self, method)(args)
        except AttributeError:
            return 'The given action does not exist.'

    def start_ftp(self):
        command = "sudo service vsftpd restart"
        cmd.getstatusoutput(command)[1]

    def _receive(self):
        # receive data from the server
        data = ""
        while True:
            part = self.connection.recv(self.model.buffer_size)
            data += part
            if len(part) < self.model.buffer_size:
                break
        return data
    
if __name__ == "__main__":
    server = SMRC_Server()
    server.start()
