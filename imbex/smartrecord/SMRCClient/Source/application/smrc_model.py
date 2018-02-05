"""
.. module: smrc_model
.. moduleauthor: Marcel Kennert
"""
from logging import getLogger
from os import walk
from os.path import basename, join, abspath
from zipfile import ZipFile, ZIP_DEFLATED

from pyface.image_resource import ImageResource
from traits.api import HasTraits, Instance, Bool, Str
from traitsui.api import View, UItem, VGroup, HGroup, Image

from application.configuration import \
    experiment_dir, experiment_ext, ext_pairs, storage_temp_dir, project_ext,\
    images_dir, strain_exx_file, strain_exx_dir, strain_exx_img_file, \
    strain_exy_dir, strain_exy_file, strain_exy_img_file, strain_eyy_dir,\
    strain_eyy_file, strain_eyy_img_file, toolbar_background
from application.smrc_handler import SMRCHandler
from basic_modules.basic_classes import InstanceUItem
from basic_modules.basic_dialogs import ProcessDialog, WarningDialog
from basic_modules.basic_methods import \
    resize_image, create_strain_images, \
    get_all_files, clear_folder,\
    clear_temp_folder, resize_strain_images
from camera.camera_selector import CameraSelector
from experiment._experiment import Experiment
from server.smrc_server import SMRCServer


class SMRCModel(HasTraits):
    """
    The object SMRCModel manages the course of the experiment. 
    It contains a model and a handler. The handler make sure that 
    the a experiment can not restart while it is running.
    The model contains the phases and address the measuring 
    card if the camera should take a picture. 
    """

    #=========================================================================
    # Important components to interact
    #=========================================================================

    experiment = Instance(Experiment)

    server = Instance(SMRCServer)

    camera = Instance(CameraSelector, ())

    #=========================================================================
    # Properties of the model
    #=========================================================================

    record_mode = Bool()

    logger = getLogger("Application")

    def __init__(self, record_mode):
        self.logger.debug("Initializes SMRCModel")
        self.server = SMRCServer(self)
        self.record_mode = record_mode
        SMRCHandler.record_mode = record_mode
        self.experiment = Experiment(self, record_mode)
        self.smrc_window = None

    def is_valid(self):
        """Checks whether the experiment is valid"""
        return self.experiment.is_valid()

    #=========================================================================
    # Toolbar actions
    #=========================================================================

    def _start(self):
        """Starts the experiment."""
        if self.server.connected:
            self.experiment_name = self.experiment.get_name()
            if self.server.check_project(self.experiment_name):
                raise ValueError("The project does already exists")
            self.send_experiment_properties()
        else:
            msg = ("The application is not connect with the server."
                   "Do you want start the experiment in the offline-mode?")
            process = WarningDialog(msg)
            if not process.open():
                return
        self.started = True
        self.experiment._start()

    def _cancel(self):
        """Cancels the experiment."""
        self.started = False
        self.experiment._cancel()

    def _manually_trigger(self):
        """Records and trigger all ports."""
        self.experiment.use_all_ports()

    #=========================================================================
    # Configuration actions
    #=========================================================================
    
    def _configure_server(self):
        """Opens a dialog to configure the server-properties"""
        self.server.connector.show_configuration()

    #=========================================================================
    # File actions
    #=========================================================================

    def save_experiment(self, fpath):
        """Saves the attributes of the experiment.

        :param fpath: Path to the file
        :type fpath: string
        :returns: True, if the experiment was saved, False otherwise
        :rtype: bool
        """
        try:
            exp_name = self.experiment.save_experiment()
            self.zip_files(experiment_dir, fpath, exp_name, experiment_ext)
        except Exception, e:
            self.logger.error(str(e))
            return False
        return True

    def save_project(self, fpath):
        """Save the project

        :param fpath: Path to the file
        :type fpath: string
        :returns: True, if the experiment was saved, False otherwise
        :rtype: bool
        """
        n = len(ext_pairs)
        exp_name = self.experiment.save_all_components()
        progress = ProcessDialog(title="Save project", max_n=n)
        try:
            for i in range(n):
                d, ext = ext_pairs[i]
                progress.update(i, "Save: {0}".format(d))
                self.zip_files(d, storage_temp_dir, exp_name + ext, "zip")
            self.zip_files(storage_temp_dir, fpath, exp_name, project_ext)
            progress.close()
        except Exception, e:
            progress.close()
            self.logger.error(str(e))
            return False
        return True

    def load_project(self, fpath="", from_server=False, project=''):
        """Loads the project

        :param fpath: Name of the file
        :type fpath: string
        :param from_server: True if the project should be load from the server
        :type from_server: Bool
        :param project: Name of the project
        :type project: string
        """
        clear_temp_folder()
        try:
            if from_server:
                self.logger.debug("Load project from server")
                self.load_project_from_server(project)
            else:
                self.logger.debug("Load project from file: {0}".format(fpath))
                self._extract_files(fpath)
            suc = self.experiment.load_project()
            clear_folder(storage_temp_dir)
            self.logger.debug("Loaded successfully [SMRCModel]")
        except Exception, e:
            self.logger.error(str(e))
            self.logger.debug("Can not load the project : {0}".format(e))
            return False
        return suc

    def load_project_from_server(self, project):
        self.logger.debug("Download project from server")
        self.server.download_project(project)
        files = get_all_files(images_dir)
        n = len(files)
        progress = ProcessDialog(title="Resize images", max_n=n)
        for i in range(n):
            f = files[i]
            self.logger.debug("Resize image: {0}".format(f))
            progress.update(i, "Resize image: {0}".format(f))
            try:
                resize_image(join(images_dir, f), True, True)
            except Exception:
                resize_image(join(images_dir, f))
        progress.close()
        self.create_strain_files()
        

    def create_strain_files(self):
        self.logger.debug("Checks whether the strain-files are loaded")
        create_strain_images(strain_exx_dir, strain_exx_file,
                             strain_exx_img_file)
        create_strain_images(strain_exy_dir, strain_exy_file,
                             strain_exy_img_file)
        create_strain_images(strain_eyy_dir, strain_eyy_file,
                             strain_eyy_img_file)
        resize_strain_images()

    def show_warning_files(self):
        msg = ("Some files are missing. Do you want generate this files?"
               " The process takes several minutes")
        pdialog = WarningDialog(msg)
        return pdialog.open()

    def _extract_files(self, fpath):
        self.logger.debug("Extract files")
        archive = ZipFile(fpath, 'r')
        archive.extractall(storage_temp_dir)
        archive.close()
        exp_name = basename(fpath).split('.')[0]
        n = len(ext_pairs)
        progress = ProcessDialog(title="Extract files", max_n=n)
        try:
            for i in range(n):
                d, ext = ext_pairs[i]
                folder = "{0}{1}.zip".format(exp_name, ext)
                progress.update(i, "Extract {0}".format(folder))
                archive = ZipFile(join(storage_temp_dir, folder), 'r')
                archive.extractall(d)
                archive.close()
            progress.close()
        except Exception, e:
            self.logger.error(str(e))
            progress.close()
            return False
        return True

    def load_experiment(self, fpath):
        archive = ZipFile(fpath, 'r')
        archive.extractall(experiment_dir)
        archive.close()
        try:
            self.experiment.load_experiment()
        except Exception, e:
            self.logger.error(str(e))
            return False
        return True

    def zip_files(self, src_path, dst_path, exp_name, extension):
        fname = "{0}/{1}.{2}".format(dst_path, exp_name, extension)
        zf = ZipFile(fname, "w", ZIP_DEFLATED)
        abs_src = abspath(src_path)
        for dirname, _, files in walk(src_path):
            for filename in files:
                absname = abspath(join(dirname, filename))
                arcname = absname[len(abs_src) + 1:]
                self.logger.debug('zipping {0} as {1}'.format(
                    join(dirname, filename), arcname))
                zf.write(absname, arcname)
        zf.close()

    def get_user_serie_type(self):
        return self.experiment.get_user_serie_type()
    
    def get_type_serie(self):
        return self.experiment.get_type_serie()
    
    def serie_created(self, experiment):
        self.experiment.serie_created(experiment)

    #=========================================================================
    # Methods to interact with the server
    #=========================================================================

    def send_experiment_properties(self):
        self.logger.debug("Send the properties of the experiment [SMRCModel]")
        exp_name = self.experiment.save_experiment()
        t, s = self.experiment.type.get_type_serie()
        fpath = '{0}/{1}/{2}'.format(t, s, exp_name)
        self.experiment.correlation_properties.save()
        self.server.send_experiment_properties(fpath)

    def send_image(self, img_name, project):
        self.logger.debug("Upload {0} [SMRCModel]".format(img_name))
        self.experiment.recorder.recorder.save()
        self.server.upload_image(img_name, project)

    def update_series(self, experiment):
        return self.server.update_series(experiment)
    
    def get_server_properties(self):
        return self.server.get_properties()
    
    def update_server_properties(self, args):
        self.server.update_properties(args)
    #=========================================================================
    # Traitsview
    #=========================================================================

    not_saved = Bool(False)

    started = Bool(False)

    icon = Image(ImageResource("../../icons/smrc_icon.png"))

    smrc = Str("SmartRecord")

    spacing = Str("\t")

    view = View(
        VGroup(
            HGroup(
                VGroup(
                    HGroup(
                        UItem('smrc',
                              style_sheet="*{font: bold; font-size:32px;\
                              color:" + toolbar_background + ";}",
                              style='readonly'),
                        UItem('icon'),
                        visible_when="not record_mode"
                    ),
                    UItem("experiment", style="custom"),
                ),
                VGroup(
                    HGroup(
                        UItem('smrc',
                              style_sheet="*{font: bold; font-size:32px;\
                              color:" + toolbar_background + ";}",
                              style='readonly'),
                        UItem('icon'),
                        visible_when="record_mode"
                    ),
                    VGroup(
                        UItem('spacing',
                              style_sheet="*{font: bold; font-size:45px;\
                              color:" + toolbar_background + ";}",
                              style='readonly', visible_when="not record_mode"),
                        InstanceUItem("server", width=150),
                        InstanceUItem("camera", width=150,
                                      visible_when="record_mode")
                    )
                )
            ),
            layout="normal"
        )
    )
