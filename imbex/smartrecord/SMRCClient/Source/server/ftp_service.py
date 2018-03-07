"""
.. module: ftp_service
.. moduleauthor: Marcel Kennert
"""
from base64 import b64decode
from ftplib import FTP
from logging import getLogger
from os.path import dirname, basename, join

from traits.api import HasTraits, Str, Int, Bool
from traitsui.api import View, Item, VGroup

from application.configuration import temp_dir, ftp_experiments, experiment_dir,\
    corr_properties_dir, recorder_dir, recording_file, recorder_file, images_dir
from application.ftp_configuration import all_server_folders, download_folders,\
    experiment_folder, properties_folder, recorder_folder, images_folder
from basic_modules.basic_dialogs import ProcessDialog, ErrorDialogs,\
    WarningDialog
from basic_modules.basic_methods import get_all_files
from server.projecthandler import \
    Serie, Experiment, ExperimentType


class FTPServer(HasTraits):

    #=========================================================================
    # Server attributes
    #=========================================================================

    host = Str("134.130.81.25")

    port = Int(5871)

    username = Str("ZnRw")

    password = Str("IW1iMUBGVFA3")

    source_path = Str("/home/ftp/smartrecord")

    logger = getLogger("Application")

    connected = Bool(False)

    def __init__(self):
        self.logger.debug("Initialize FTPServer")
        self.connect()

    def connect(self):
        self.logger.debug("Try to connect with the FTP-server.")
        try:
            self.ftp = FTP(self.host)
            self.ftp.login(b64decode(self.username), b64decode(self.password))
            self.connected = True
            self.logger.debug("Connected [FTPServer]")
        except Exception, e:
            self.logger.error(str(e))
            self.connected = False
            return False
        return True

    #=========================================================================
    # create-methods
    #=========================================================================

    def create_serie(self, exp_type, serie_name):
        basepath = exp_type
        self.ftp.cwd(basepath)
        self.ftp.mkd(serie_name)
        

    def send_project(self, t, serie, project):
        basepath = self.source_path+ ftp_experiments+'/' + \
            t + '/' + serie + '/' + project
        print basepath
        try:
            if self.connect():
                try:
                    self.ftp.mkd(basepath)
                    for d in all_server_folders:
                        dir_path = dirname(d)
                        dir_name = basename(d)
                        self.ftp.cwd(basepath + '/' + dir_path)
                        self.ftp.mkd(dir_name)
                except Exception:
                    w=WarningDialog("The project does alread exists. Do you want overrite the files?")
                    if not w.open():
                        raise ValueError()
                n = len(download_folders)
                progress = ProcessDialog(title="Upload project", max_n=n)
                for i in range(n):
                    d = download_folders[i]
                    source = basepath + '/' + d
                    print source
                    progress.update(i, 'Upload: {0}'.format(basename(source)))
                    self.ftp.cwd(source)
                    exist_files = self.ftp.nlst()
                    files = get_all_files(join(temp_dir, d))
                    for f in files:
                        if not f in exist_files:
                            fpath = join(temp_dir, d, f)
                            self.ftp.storbinary("STOR " + f, open(fpath, 'rb'))
                progress.close()
            else:
                progress.close()
                raise Exception(
                    "The connection with the FTP-Service is interrupt")
        except Exception, e:
            self.logger.error(str(e))
            errordialog = ErrorDialogs()
            errordialog.open_error("The project does already exists")

    #=========================================================================
    # Load-methods
    #=========================================================================

    def load_types(self):
        basepath = self.source_path + ftp_experiments
        self.ftp.cwd(basepath)
        return self.ftp.nlst()

    def load_series(self, exp_type):
        basepath = self.source_path + ftp_experiments + '/' + exp_type
        self.ftp.cwd(basepath)
        return self.ftp.nlst()

    def load_projects(self):
        try:
            self.connect()
            basepath = self.source_path + ftp_experiments
            self.ftp.cwd(basepath)
            res = []
            for exp_type in self.ftp.nlst():
                exp_path = "{0}/{1}".format(basepath, exp_type)
                self.ftp.cwd(exp_path)
                experiment_type = ExperimentType(name=exp_type, path=exp_path)
                res.append(experiment_type)
                for serie in self.ftp.nlst():
                    ser_path = "{0}/{1}".format(exp_path, serie)
                    self.ftp.cwd(ser_path)
                    s = Serie(name=serie, path=ser_path)
                    experiment_type.series.append(s)
                    for exp in self.ftp.nlst():
                        p = "{0}/{1}".format(ser_path, exp)
                        s.experiments.append(Experiment(name=exp, path=p))
        except Exception, e:
            self.logger.error(str(e))
        return res

    #=========================================================================
    # Methods to handle the projects
    #=========================================================================

    def update_series(self, experiment):
        try:
            basepath = self.source_path + '/' + \
                ftp_experiments + '/' + experiment
            self.ftp.cwd(basepath)
        except Exception:
            self.logger.error(
                "The application can not connect with the servers")
            return []
        return self.ftp.nlst()

    def upload_start_properties(self, project):
        """Upload the experiment properties"""
        project = ftp_experiments + '/' + project
        try:
            if self.connect():
                self.create_folders(project)
                self.upload_correlation_properties(project)
                self.upload_experiment(project)
                self.upload_references_image(project)
            else:
                raise Exception(
                    "The connection with the FTP-Service is interrupt")
        except Exception, e:
            self.logger.error(str(e))

    def create_folders(self, project):
        """Creates all folders on the server"""
        try:
            if self.connect():
                self.ftp.cwd(self.source_path)
                basepath = self.source_path + '/' + project
                self.ftp.mkd(basepath)
                for d in all_server_folders:
                    dir_path = dirname(d)
                    dir_name = basename(d)
                    self.ftp.cwd(basepath + '/' + dir_path)
                    self.ftp.mkd(dir_name)
            else:
                raise Exception(
                    "The connection with the FTP-Service is interrupt")
        except Exception, e:
            self.logger.error(str(e))

    def upload_experiment(self, project):
        """Upload the experiment properties"""
        try:
            if self.connect():
                files = get_all_files(experiment_dir)
                basepath = self.source_path + '/' + project
                self.ftp.cwd(basepath + '/' + experiment_folder)
                for f in files:
                    fpath = join(experiment_dir, f)
                    self.ftp.storbinary("STOR " + f, open(fpath, 'rb'))
            else:
                raise Exception(
                    "The connection with the FTP-Service is interrupt")
        except Exception, e:
            self.logger.error(str(e))

    def upload_correlation_properties(self, project):
        """Upload the experiment properties"""
        try:
            if self.connect():
                files = get_all_files(corr_properties_dir)
                basepath = self.source_path + '/' + project
                self.ftp.cwd(basepath + '/' + properties_folder)
                for f in files:
                    fpath = join(corr_properties_dir, f)
                    self.ftp.storbinary("STOR " + f, open(fpath, 'rb'))
            else:
                raise Exception(
                    "The connection with the FTP-Service is interrupt")
        except Exception, e:
            self.logger.debug(str(e))

    def upload_recordings(self, project):
        """Upload the experiment properties"""
        self.logger.debug("Upload recordings")
        try:
            if self.connect():
                self.ftp.cwd(project + '/' + recorder_folder)
                fpath = join(recorder_dir, recording_file)
                self.ftp.storbinary(
                    "STOR " + recording_file, open(fpath, 'rb'))
                fpath = join(recorder_dir, recorder_file)
                self.ftp.storbinary("STOR " + recorder_file, open(fpath, 'rb'))
                fpath = join(recorder_dir, recording_file)
                self.ftp.storbinary(
                    "STOR " + recording_file, open(fpath, 'rb'))
            else:
                raise Exception(
                    "The connection with the FTP-Service is interrupt")
        except Exception, e:
            self.logger.debug(str(e))

    def upload_references_image(self, project):
        """Upload the reference image"""
        try:
            if self.connect():
                files = get_all_files(images_dir)
                basepath = self.source_path + '/' + project
                self.ftp.cwd(basepath + '/' + images_folder)
                for f in files:
                    fpath = join(images_dir, f)
                    self.ftp.storbinary("STOR " + f, open(fpath, 'rb'))
            else:
                raise Exception(
                    "The connection with the FTP-Service is interrupt")
        except Exception, e:
            self.logger.error(str(e))

    def upload_image(self, img_name, project):
        """Upload the image of the given project"""
        self.logger.debug("Upload {0}".format(img_name))
        basepath = self.source_path + '/' + ftp_experiments + '/' + project
        try:
            if self.connect():
                self.ftp.cwd(basepath + '/' + images_folder)
                fpath = join(images_dir, img_name)
                self.ftp.storbinary("STOR " + img_name, open(fpath, 'rb'))
                self.upload_recordings(basepath)
            else:
                raise Exception(
                    "The connection with the FTP-Service is interrupt")
        except Exception, e:
            self.logger.error(str(e))

    def upload_all_images(self, project):
        self.logger.debug("Upload all images")
        basepath = self.source_path + '/' + ftp_experiments + '/' + project
        try:
            if self.connect():
                self.ftp.cwd(basepath + '/' + images_folder)
                for img_name in get_all_files(images_dir):
                    fpath = join(images_dir, img_name)
                    self.ftp.storbinary("STOR " + img_name, open(fpath, 'rb'))
                    self.upload_recordings(basepath)
            else:
                raise Exception(
                    "The connection with the FTP-Service is interrupt")
        except Exception, e:
            self.logger.error(str(e))

    def upload_project(self, project):
        """Upload the project"""
        try:
            self.upload_experiment(project)
            self.upload_correlation(project)
            self.upload_recordings(project)
        except Exception, e:
            self.logger.error(str(e))

    def download_project(self, project):
        """Creates all folders on the server"""
        self.logger.debug("Download project: {0}".format(project))
        try:
            basepath = project
            n = len(download_folders)
            progress = ProcessDialog(title="Download project", max_n=n)
            for i in range(n):
                d = download_folders[i]
                source = basepath + '/' + d
                progress.update(i, 'Download: {0}'.format(basename(source)))
                self.ftp.cwd(source)
                files = self.ftp.nlst()
                for fname in files:
                    fpath = join(temp_dir, d, fname)
                    self.logger.debug("Download file : {0}".format(fname))
                    with open(fpath, 'wb') as f:
                        self.ftp.retrbinary('RETR ' + fname, f.write)
        except Exception, e:
            self.logger.error(e)
            progress.close()
            return False
        progress.close()
        return True

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    view = View(
        VGroup(
            Item('host')
        )
    )
