"""
.. module: experiment_handler
.. moduleauthor: Marcel Kennert
"""
from logging import getLogger
from time import sleep

from traits.api import HasTraits, Instance, Bool, Str
from traitsui.api import View, UItem, Image, VGroup, HGroup, spring

from application.configuration import images_dir
from experiment.correlation.correlation_properties import CorrelationProperties
from experiment.recorder.experiment_recorder import ExperimentRecorder
from experiment.type.experiment_type import ExperimentType
from basic_modules.basic_methods import get_all_files
from basic_modules.basic_dialogs import ErrorDialogs, ProcessDialog


class Experiment(HasTraits):
    """
    The Experiment handles the interaction with the recorder 
    of the application. The handler makes sure that a experiment can not 
    started while it"s running. Furthermore the handler checks 
    whether the experiment has all require properties before 
    it can start.
    """

    #=========================================================================
    # Important components to interact
    #=========================================================================

    recorder = Instance(ExperimentRecorder)

    correlation_properties = Instance(CorrelationProperties)

    type = Instance(ExperimentType, ())

    error_dialog = ErrorDialogs()

    #=========================================================================
    # Properties of the experiment
    #=========================================================================

    started = Bool(False)

    canceled = Bool(False)

    record_mode = Bool()

    logger = getLogger("Application")

    def __init__(self, parent, record_mode):
        self.logger.debug("Initialize Experiment")
        self.record_mode = record_mode
        self.smrc_model = parent
        camera = self.smrc_model.camera
        camera.add_listener(self)
        self.correlation_properties = CorrelationProperties(self)
        self.recorder = ExperimentRecorder(self, record_mode, camera)
        self.type.exp_model = self
        self.type.record_mode = record_mode
        self.type.update_series()

    #=========================================================================
    # Methods to provide important data for other components
    #=========================================================================

    def save(self):
        """Returns the properties of the experiment body"""
        return self.type.save()

    def get_correlation_properties(self):
        """Returns the properties for the correlation"""
        return self.correlation_properties.save()

    def get_recorded_values(self):
        """Returns the recorded values"""
        return self.recorder.recorder.get_values()

    def get_user_serie_type(self):
        """Returns the series of the type"""
        return self.type.get_user_serie_type()
    
    def get_type_serie(self):
        return self.type.get_type_serie()
    
    def serie_created(self, experiment):
        print experiment
        self.type.update_series(experiment)
    #=========================================================================
    # Methods to interact with the Server
    #=========================================================================

    def update_series(self, experiment):
        """Updates the series of the given experiment-type

        :param experiment: Experiment-type
        :type experiment: string
        """
        return self.smrc_model.update_series(experiment)

    def send_image(self):
        """Sends the last recorded image to the server"""
        img_file = get_all_files(images_dir)[-1]
        t, s = self.type.get_type_serie()
        project = t + '/' + s + '/' + self.type.generate_file_name()
        self.smrc_model.send_image(img_file, project)

    #=========================================================================
    # Methods to check the components
    #=========================================================================

    def is_valid(self):
        """Checks whether the components of the experiment are valid"""
        self.recorder.is_valid()
        self.correlation_properties.is_valid()
        self.recorder.is_valid()

    def measuring_card_is_valid(self):
        """Checks whether the measuring card is valid"""
        self.recorder.measuring_card.is_valid()

    #=========================================================================
    # Methods to interact with the camera
    #=========================================================================

    def create_reference_image(self):
        """Takes the reference image and transfer the image to the camera"""
        progress = ProcessDialog(title="Transfer image", max_n=2)
        self.recorder.measuring_card.trigger_all_ports()
        progress.update(1, "Download image")
        self.smrc_model.camera.download_reference_image()
        progress.close()
        return True

    def update_reference(self, f):
        """Updates the reference image"""
        self.recorder.update_reference(f)

    #=========================================================================
    # Methods to interact with the ExperimentHandler
    #=========================================================================

    def save_all_components(self):
        exp_name = self.save_experiment()
        self.recorder.recorder.save()
        self.correlation_properties.save()
        return exp_name

    def save_experiment(self):
        self.recorder.save_experiment()
        exp_name = self.type.save()
        return exp_name

    def load_project(self):
        try:
            self.load_experiment()
            self.recorder.load_components()
        except Exception, e:
            self.logger.error(str(e))
            return False
        return True

    def load_experiment(self):
        self.type.load()
        self.recorder.load_experiment()

    #=========================================================================
    # Methods for the recording
    #=========================================================================

    def _start(self):
        # Checks whether the experiment have all require informations
        # and is not running. If there are no conflicts, the recorder will
        # start.
        if self._check_attributes():
            self.reset_properties()
            self.recorder.start()
            self.window.start_clock()

    def _cancel(self):
        # Cancel the recording and stop the clock of
        # the window.
        self.recorder.editor._cancel_record()
        self._finished_experiment()

    def _manually_trigger(self):
        # trigger a digital output signal to the measuring
        # card and read all values of the input ports
        self.recorder.use_all_ports()

    def _check_attributes(self):
        # Checks whether the measuring card have a input port and
        # a output port. Furthermore the method checks whether
        # the ExperimentRecorder have phases.
        if len(self.recorder.measuring_card.input_ports) < 1 or \
                len(self.recorder.editor.phases) < 1 \
                or len(self.recorder.measuring_card.output_ports) < 1:
            self.error_dialog.configure_traits(kind="livemodal")
            return False
        return True

    def reset_properties(self):
        # set the properties for the start
        self.recorder.not_saved = True
        self.started = True
        self.canceled = True
        self.start_time = None

    def use_all_ports(self):
        self.recorder.use_all_ports()

    def get_values_as_string(self):
        return self.recorder.measuring_card.get_values_as_string()

    def get_name(self):
        return self.type.name

    #=========================================================================
    # Methods to show the state of the ExperimentRecorder
    #=========================================================================

    def update_downloaded_image(self, fname):
        self.send_image()

    def update_downloaded_preview(self, fpath):
        pass

    def _finished_experiment(self):
        # Updates the User Interface that the experiment is finished.
        self.window.clock_running = self.started = False
        self.canceled = False
        self.window.current_phase = "Finished"

    def _update_values(self):
        # Show the current recorded values of all ports.
        while self.started:
            self.recordings = self.get_values_as_string()
            sleep(0.3)

    def _update_icon(self, time_interval=0.6):
        # Show the camera-icon for the given time_interval.
        self.recording = True
        sleep(time_interval)
        self.recording = False

    def update_phase(self, name):
        # Update the phase of the SMRC-Window
        self.smrc_model.smrc_window.current_phase = name

    def get_time(self):
        return self.smrc_model.smrc_window.clock

    #=========================================================================
    # Traitsview
    #=========================================================================

    camera_icon = Image("../icons/camera.png")

    recording = Bool(False)

    recordings = Str()

    view = View(
        VGroup(
            HGroup(
                UItem("recordings", style="readonly",
                      style_sheet="*{font: bold; font-size:25px;}"),
                spring,
                UItem("camera_icon", visible_when="recording"),
                visible_when="record_mode"
            ),
            HGroup(
                UItem("recorder", style="custom")
            )
        )
    )
