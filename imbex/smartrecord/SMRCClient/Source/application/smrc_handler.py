"""
.. module: smrc_handler
.. moduleauthor: Marcel Kennert
"""
from logging import getLogger
from os.path import realpath, join, getmtime, basename
from shutil import copy
from sys import exit
from webbrowser import open

from PySide.QtCore import Qt
from PySide.QtGui import QMainWindow
from cv2 import imread
from pyface.constant import OK
from pyface.file_dialog import FileDialog
from pyface.image_resource import ImageResource
from traits.api import Instance
from traitsui.api import Handler, UIInfo, Action
from traitsui.menu import Separator

from application.configuration import \
    experiment_ext, project_ext, stylesheet_smrc, images_dir, image_file,\
    udisplacement_file, vdisplacement_file, strain_exx_dir, strain_exx_file,\
    strain_exy_dir, strain_exy_file, strain_eyy_dir, strain_eyy_file,\
    strain_exx_img_file, displacement_v_dir, displacement_u_dir,\
    strain_exy_img_file, strain_eyy_img_file
from basic_modules.basic_dialogs import ApplicationDialogs, ImportManuallyLoader,\
    ProcessDialog
from basic_modules.basic_methods import convert_number, get_all_files,\
    create_strain_images, resize_strain_images
from experiment.recorder.phase_editor.phase_container import PhaseEditor
from experiment.recorder.recording._recorder import Recorder
from experiment.type.experiment_type import ExperimentType
from server.smrc_server import ServerDialog
from measuring_card.card import MeasuringCard


file_save_project = Action(action="save_project", name="Save project")

file_load_project = Action(action="load_project", name="Load project")

file_save_experiment = Action(action="save_experiment", name="Save experiment")

file_load_experiment = Action(action="load_experiment", name="Load experiment")

file_exit = Action(action="exit", name="Exit")

conf_server = Action(action="conf_server", name="Server configuration")

help_docs = Action(action="open_tutorial", name="Tutorial")

import_project = Action(action="import_project", name="Import project")

import_dic_results = Action(
    action="import_dic_results", name="Import DIC-results")


class SMRCHandler(Handler):
    """Handles the interaction with the SMRCModel and the SMRCWindow."""

    # dialogs to interact with the user
    application_dialogs = ApplicationDialogs()

    server_dialog = ServerDialog()

    # The UIInfo object associated with the view
    info = Instance(UIInfo)

    logger = getLogger("Application")

    def init(self, info):
        info.ui.control.setContextMenuPolicy(Qt.NoContextMenu)
        for c in info.ui.control.children():
            if isinstance(c, QMainWindow):
                c.setContextMenuPolicy(Qt.NoContextMenu)
        info.ui.control.setStyleSheet(stylesheet_smrc)
        self.logger.debug("Finished initializing")

    def object_record_mode_changed(self, info):
        if not info.object.record_mode:
            info.ui.view.toolbar.visible = False
            info.object.current_phase = "Evaluate-mode"
            info.object.clock = ""

    def close(self, info, is_ok):
        self.exit(info)
    #=========================================================================
    # Toolbar actions
    #=========================================================================

    def _start(self, info):
        """Starts the record-process."""
        if info.object.model.not_saved:
            confirm = self.application_dialogs.open_restart()
            if not confirm:
                return
        try:
            info.object.model.is_valid()
            self.logger.info("Start the experiment. [SMRCHandler]")
            info.object.model._start()
            info.object.model.not_saved = True
        except ValueError, e:
            self.logger.error(str(e))
            self.application_dialogs.open_error(str(e))

    def _cancel(self, info):
        """Cancels the record-process."""
        if info.object.model.record_mode:
            self.logger.info("Cancel the experiment [SMRCHandler]")
            info.object.model._cancel()

    def _manually_trigger(self, info):
        """Records a image."""
        if info.object.model.record_mode:
            self.logger.info("Manually trigger [SMRCHandler]")
            info.object.model._manually_trigger()

    #=========================================================================
    # File actions
    #=========================================================================

    def save_project(self, info):
        """Saves the project."""
        self.logger.info("Save the project [SMRCHandler]")
        fpath = self.application_dialogs.save_dialog.open()
        if fpath != None:
            suc = info.object.model.save_project(fpath)
            self.application_dialogs.open_state(suc)

    def save_experiment(self, info):
        """Saves the experiment."""
        self.logger.info("Save the experiment [SMRCHandler]")
        fpath = self.application_dialogs.save_dialog.open()
        if fpath != None:
            suc = info.object.model.save_experiment(fpath)
            self.application_dialogs.open_state(suc)

    def load_experiment(self, info):
        """Loads the experiment."""
        self.logger.info("Load a experiment [SMRCHandler]")
        fdlg = FileDialog(wildcard="*{0}".format(experiment_ext),
                          title="Choose experiment")
        if fdlg.open() == OK:
            suc = info.object.model.load_experiment(fdlg.path)
            if not suc:
                self.application_dialogs.open_state(suc)

    def load_project(self, info):
        """Loads the project."""
        self.logger.info("Load a project [SMRCHandler]")
        fdlg = FileDialog(wildcard="*{0}".format(project_ext),
                          title="Choose experiment")
        if fdlg.open() == OK:
            info.object.model.not_saved = True
            suc = info.object.model.load_project(fdlg.path)
            if not suc:
                self.application_dialogs.open_state(suc)

    def exit(self, info):
        # open a dialog to ask whether the view should be
        # terminate.
        confirm = self.application_dialogs.open_exit()
        if confirm:
            self.logger.info("Application was closed [SMRCHandler]")
            exit()

    #=========================================================================
    # Configuration actions
    #=========================================================================

    def conf_server(self, info):
        self.logger.info("Configure the server-configurations [SMRCHandler]")
        host, port = info.object.model.get_server_properties()
        self.server_dialog.set_attributes(host, port)
        if self.server_dialog.open_dialog():
            args = self.server_dialog.get_attributes()
            info.object.model.update_server_properties(args)
    #=========================================================================
    # Help actions
    #=========================================================================

    def import_project(self, info):
        try:
            exp_model = info.object.model.experiment
            if not ExperimentType.open(exp_model):
                return
            MeasuringCard.generate_input_port()
            fdlg = FileDialog(wildcard="*.*".format(project_ext),
                              title="Select images", action='open files')
            if fdlg.open() == OK:
                files = sorted(fdlg.paths)
                values = self.copy_images(files)
                iloader = ImportManuallyLoader(values)
                if iloader.configure_traits(kind="livemodal"):
                    imgs, vals = iloader.get_images_values()
                    Recorder.save_images(imgs)
                    Recorder.save_values(vals)
                    PhaseEditor.generate_phases()
                    info.object.model.experiment.load_project()
        except Exception:
            msg = (
                "The import process can not be done. Make sure you are connected with the servers.")
            self.application_dialogs.open_error(msg)

    def import_dic_results(self, info):
        try:
            f = get_all_files(images_dir)[0]
            imread(join(images_dir, f)).shape[:2]
            files = [("u-displacements", displacement_u_dir, udisplacement_file),
                     ("v-displacements", displacement_v_dir,
                      vdisplacement_file),
                     ("strain-exx", strain_exx_dir, strain_exx_file),
                     ("strain-exy", strain_exy_dir, strain_exy_file),
                     ("strain-eyy", strain_eyy_dir, strain_eyy_file)]
            for f in files:
                if not self.copy_files(*f):
                    return
            create_strain_images(strain_exx_dir, strain_exx_file,
                                 strain_exx_img_file)
            create_strain_images(strain_exy_dir, strain_exy_file,
                                 strain_exy_img_file)
            create_strain_images(strain_eyy_dir, strain_eyy_file,
                                 strain_eyy_img_file)
            resize_strain_images()
        except Exception, e:
            self.logger.error(str(e))
            self.application_dialogs.open_error(msg="Can not find images")
            return

    def copy_files(self, fnames, dst_path, fname):
        fdlg = FileDialog(wildcard="*.csv*", title="Select {0}".format(fnames),
                          action='open files')
        if fdlg.open() == OK:
            files = sorted(fdlg.paths)
            progress = ProcessDialog(title="Copy file", max_n=len(files))
            for i in range(1, len(files)):
                f = files[i]
                progress.update(i, msg="Copy file: {0}".format(basename(f)))
                dst_file = fname.format(convert_number(i))
                dst = join(dst_path, dst_file)
                copy(f, dst)
            progress.close()
            return True
        return False

    def copy_images(self, files):
        values = []
        ref_time = getmtime(files[0])
        progress = ProcessDialog(title="Copy image", max_n=len(files))
        for i in range(len(files)):
            f = files[i]
            progress.update(i, msg="Copy file: {0}".format(basename(f)))
            ext = "." + f.split('.')[-1]
            dst_file = image_file.format(convert_number(i), ext)
            dst = join(images_dir, dst_file)
            copy(f, dst)
            values.append((dst_file, getmtime(f) - ref_time))
        progress.close()
        return values

    #=========================================================================
    # Help actions
    #=========================================================================

    def open_tutorial(self, info):
        """Opens the tutorial for the application"""
        self.logger.info("Open the tutorial [SMRCHandler]")
        path = realpath("../../docs/_build/html/tutorial.html")
        html_file = "file://" + path
        open(html_file, new=2)


toolbar_actions = [Action(action="_start",
                          image=ImageResource("../../icons/run.png"),
                          enabled_when="not model.started"),
                   Action(action="_cancel",
                          image=ImageResource("../../icons/stop.png"),
                          enabled_when="model.started"),
                   Action(action="_manually_trigger",
                          image=ImageResource("../../icons/manually.png"),
                          enabled_when="model.started")]

file_actions = [file_exit, Separator(), file_save_experiment, file_save_project,
                Separator(), file_load_experiment, file_load_project,
                Separator()]

configure_actions = [conf_server]

import_action = [import_project, import_dic_results]
