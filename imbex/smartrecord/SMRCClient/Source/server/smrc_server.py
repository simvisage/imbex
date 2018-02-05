"""
.. module: server_handler
.. moduleauthor: Marcel Kennert
"""
from __builtin__ import True
import logging
import socket
from json import dump, load
from traits.api import Str, HasTraits, Instance, List, Bool, Int, Button
from traitsui.api import View, VGroup, UItem, Item, HGroup
from os.path import exists, basename
from application.configuration import server_dir
from basic_modules.basic_classes import RunThread, InstanceUItem
from server.ftp_service import FTPServer
from server.projecthandler import ProjectHandler
import time
from basic_modules.basic_dialogs import ErrorDialogs


class ServerDialog(HasTraits):
    """not finished yet"""

    host = Str()

    port = Int()

    bsize = Int()

    def open_dialog(self):
        return self.configure_traits(kind='livemodal')

    def set_attributes(self, host, port):
        """not finished yet"""
        self.host = host
        self.port = port

    def get_attributes(self):
        """not finished yet"""
        return self.host, self.port

    view = View(
        VGroup(
            Item("host"),
            Item("port"),
            label="Server"
        ),
        buttons=["OK"],
        title="Configuration"
    )


class SMRCConncetion(HasTraits):
    """Handles the connection to the server"""

    connected = Bool(False)

    try_connect = Bool(False)

    hostname = Str()

    port = Int()

    connect_btn = Button("Reconnect")

    connect_error = Str("The application can not connect with the server")

    # Directory of the configuration file. The directory will use
    # to load the attributes of the server.
    confdir = server_dir

    # Name of the configuration file
    config = "/smrc_server.json"

    # The host will use if the configuration file of the server
    # does not exists.
    hostname = Str("localhost")

    # The port will use if the configuration file of the server
    # does not exists.
    port = Int(20000)

    logger = logging.getLogger("Application")

    def __init__(self, parent):
        self.logger.debug("Initialize SMRCConncetion")
        self.dialog = ServerDialog()
        self.hostname, self.port = self.load_properties()
        self.parent = parent
        self._try_to_connect(it=1)
    
    def save(self):
        self._create_configfile(self.hostname, self.port)
        
    def load_properties(self):
        """
        Returns the properties of the server. The method reads 
        the properties from the configuration file. If the file 
        does not exist, the method will create a new configuration
        file with the default properties.

        :returns: Properties of the server
        :rtype: List
        """
        # Make sure that the needed files exists. Otherwise
        # the method will create the files with the default
        # properties of the server.
        if exists(self.confdir + self.config):
            args = self._read_configfile()
        else:
            self._create_configfile(self.hostname, self.port)
            args = [self.hostname, self.port]
        return args

    def _create_configfile(self, host, port):
        # creates the configuration file if the file
        # does not exists.
        self.logger.debug("Create configuration file for the server")
        info = {}
        info["host"] = host
        info["port"] = port
        with open(self.confdir + self.config, "w") as f:
            dump(info, f, indent=4)

    def _read_configfile(self):
        # reads the configuration file of the server
        # and returns all properties.
        with open(self.confdir + self.config) as f:
            data = load(f)
        return data["host"], data["port"]

    def _connect_btn_fired(self):
        # make it possible to connect with the server
        RunThread(target=self._try_to_connect)

    def _try_to_connect(self, it=3, projects=True):
        # try to connect with the server
        self.logger.debug("Try to connect with the server.")
        self.try_connect = True
        self.hostname, self.port = self.load_properties()
        self.connect_error = "Try to connect with the server..."
        while it > 0:
            try:
                self.parent.socket.connect((self.hostname, self.port))
                self.connected = self.parent.connected = True
                if projects:
                    self.parent.update_projects()
                self.logger.debug("Application is connected with the server")
                break
            except Exception, e:
                self.logger.error(str(e))
            it -= 1
            time.sleep(0.5)
        self.connect_error = "The application can not connect with the server"
        self.try_connect = False

    view = View(
        VGroup(
            UItem("connect_btn", enabled_when="not try_connect",
                  visible_when="not connected"),
            HGroup(
                Item("hostname", style="readonly"),
                Item("port", style="readonly")
            ),
            layout="normal",
            label="Server"
        )
    )


class SMRCServer(HasTraits):
    """Manages the communication with the SMRCServer."""

    #=========================================================================
    # Important components to interact
    #=========================================================================

    ftp_server = Instance(FTPServer, ())

    connector = Instance(SMRCConncetion)

    project_handler = Instance(ProjectHandler)

    connected = Bool(False)

    projects = List(Str)

    logger = logging.getLogger("Application")

    def __init__(self, smrc_model):
        self.logger.debug("Initialize SMRCServer")
        self.smrc_model = smrc_model
        self.project_handler = ProjectHandler(parent=self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connector = SMRCConncetion(self)

    #=========================================================================
    # Methods to handle the projects
    #=========================================================================

    def send_experiment_properties(self, project):
        """Send the properties to server"""
        self.ftp_server.upload_start_properties(project)

    def upload_image(self, img_name, experiment):
        """Uploads the given image

        :param img_name: Name of the image
        :type img_name: string
        :param experiment: Related project
        :type experiment: string
        """
        if self.connected:
            RunThread(target=self.ftp_server.upload_image,
                      args=(img_name, experiment))
        else:
            RunThread(target=self.update_project, args=[experiment])

    def update_project(self, experiment):
        self.connector._try_to_connect(3)
        if self.connected:
            if self.ftp_server.connect():
                args = self.smrc_model.get_user_serie_type()
                if not args == None:
                    _, s, t = args
                    project = "{0}/{1}/{2}".format(t, s, experiment)
                    self.send_project(project)

    def send_project(self):
        try:
            exp_name = self.smrc_model.experiment.save_all_components()
            t,serie=self.smrc_model.get_type_serie()
            self.ftp_server.send_project(t, serie, exp_name)
        except Exception:
            errordialog=ErrorDialogs()
            errordialog.open_error("Can not send the project")

    def create_serie(self, exp_type, name):
        """Creates a serie on the server

        :param exp_type: Name of the experiment-type
        :type exp_type: string
        :param name: Name of the experiment
        :type name: string
        """
        if self.is_experiment(exp_type):
            if not self.is_serie(exp_type + '/' + name):
                for exp in self.project_handler.root.experiments:
                    if exp.path == exp_type:
                        self.ftp_server.create_serie(exp_type, name)
                        self.smrc_model.serie_created(basename(exp_type))
                        return True
            else:
                msg = "The serie-name does already exists!"
                error_dialog=ErrorDialogs()
                error_dialog.open_error(msg)
                return False
        msg = "The selected folder is not a experiment-type"
        error_dialog=ErrorDialogs()
        error_dialog.open_error(msg)
        return False

    def is_serie(self, fpath):
        """Checks whether the given filepath is a path of a serie

        :param fpath: Path to the selected folder
        :type fpath: string
        :returns: True if the path belongs to a experiment, False otherwise
        :rtype: bool
        """
        for exp in self.project_handler.root.experiments:
            for s in exp.series:
                print s.path, fpath
                if s.path == fpath:
                    return True
        return False

    def is_experiment(self, fpath):
        """Checks whether the given filepath is a path of a experiment

        :param fpath: Path to the selected folder
        :type fpath: string
        :returns: True if the path belongs to a experiment, False otherwise
        :rtype: bool
        """
        for exp in self.project_handler.root.experiments:
            if exp.path == fpath:
                return True
        return False

    def load_project(self, project):
        """Load the project from the server

        :param project: Name of the project
        :type project: string
        """
        return self.smrc_model.load_project(from_server=True, project=project)

    def download_project(self, project):
        return self.ftp_server.download_project(project)

    def update_projects(self):
        """Update the projects in the projecthandler"""
        experiment_types = self.ftp_server.load_projects()
        self.project_handler.update_structure(experiment_types)

    def update_series(self, experiment):
        """Get the series of the experiment-type

        :param experiment: Experiment-type
        :type experiment: string
        :returns: All series of the experiment-type
        :rtype: List
        """
        return self.ftp_server.update_series(experiment)

    def check_project(self, project):
        """Checks whether the project name does already exists"""
        return project in self.projects

    def get_properties(self):
        """Returns the connection-properties of the server. 

        :returns: (hostname, port)
        :rtype:Tuple(string, int)
        """
        return (self.connector.hostname, self.connector.port)

    def update_properties(self, args):
        """Update the properties of the server and save them."""
        host, port = args
        self.connector.hostname = host
        self.connector.port = port
        self.connector.save()
    
    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    traits_view = View(
        VGroup(
            UItem("connector", style="custom"),
            VGroup(
                InstanceUItem("project_handler", width=50),
                enabled_when="connected"
            ),
            layout="normal",
        )
    )
