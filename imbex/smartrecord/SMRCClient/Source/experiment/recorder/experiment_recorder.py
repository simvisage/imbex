"""
.. module: experiment_model
.. moduleauthor: Marcel Kennert
"""
from json import dump, load
from logging import getLogger
from os.path import join

from traits.api import HasTraits, Instance, Bool, Int
from traitsui.api import View, Item, UItem, VGroup, HGroup

from application.configuration import \
    experiment_dir, experiment_recorder_file
from basic_modules.basic_classes import RunThread, InstanceUItem
from experiment.correlation.correlation_properties import CorrelationProperties
from experiment.recorder.eval_methods.methods import EvalMethods
from experiment.recorder.phase_editor.phase_container import PhaseEditor
from experiment.recorder.recording._recorder import Recorder
from experiment.type.experiment_type import ExperimentType
from measuring_card.card import MeasuringCard


class ExperimentRecorder(HasTraits):
    """
    The ExperimentRecorder are the component of the Experiment which 
    recorder the experiment. The Object make it possible to 
    define phases with the PhaseEditor. Furthermore it 
    address the measuring card and plot the records in a graph.
    """

    #=========================================================================
    # Important components to interact
    #=========================================================================

    measuring_card = Instance(MeasuringCard)

    recorder = Instance(Recorder)

    editor = Instance(PhaseEditor)

    eval_methods = Instance(EvalMethods)

    #=========================================================================
    # Properties to handle the upload in live-mode
    #=========================================================================

    cur_image = Int(0)

    #=========================================================================
    # Properties of the experiment
    #=========================================================================

    record_mode = Bool()

    logger = getLogger('Application')

    def __init__(self, parent, record_mode, camera_handler):
        self.logger.debug('Initializes ExperimentRecorder')
        self.record_mode = record_mode
        self.correlation_properties = parent.correlation_properties
        self.type = parent.type
        self.handler = parent
        self.recorder = Recorder(record_mode)
        self.editor = PhaseEditor(record_mode)
        self.editor.set_model(self)
        self.eval_methods = EvalMethods(self)
        if self.record_mode:
            self.camera_handler = camera_handler
            self.camera_handler.add_listener(self)
            self.measuring_card = MeasuringCard()
            self.measuring_card.model = self

    def is_valid(self):
        """Checks whether the configuration of the components are valid"""
        self.measuring_card.is_valid()
        self.editor.is_valid()

    #=========================================================================
    # Methods to handle the experiment
    #=========================================================================

    def start(self):
        """Start the experiment."""
        self.recorder.reset(self.measuring_card.input_ports)
        RunThread(target=self._start_record)

    def _start_record(self):
        # Starts the recorder of the experiment. The method
        # must call in a own thread to avoid that the gui
        # is not usable
        RunThread(target=self.handler._update_values)
        self.eval_methods.evaluate(model=self)
        

    def use_all_ports(self, reset=True, reset_time=0.1):
        """
        Records all values of the input ports and save them \
        in the recorder-object. Furthermore the method trigger 
        a digital output signal to all output ports to take a
        picture.

        :param reset: True if the port should reset, False otherwise
        :type reset: bool
        :param reset_time: Time to pass to reset the port
        :type reset_time: float
        """
        self.logger.debug(
            "Trigger and recorder all ports [ExperimentRecorder]")
        self.cur_image += 1
        self.measuring_card.trigger_all_ports(reset, reset_time)
        RunThread(target=self.handler._update_icon)
        information = self.measuring_card.record_all_ports()
        for info in information:
            self.recorder.append(info, self.handler.get_time())
        RunThread(target=self.recorder._update_plots)
        RunThread(target=self.camera_handler.download_last_image)

    #=========================================================================
    # Methods to save the experiment
    #=========================================================================

    def save_project(self):
        """Returns the port as a dictionary for a JSON file

        :returns: Dictionary with all attributes of the port
        :rtype: Dictionary
        """
        self.logger.debug("Save Project [ExperimentRecorder]")
        self.recorder.save()
        self.save_experiment()
        self.correlation_properties.save()

    def save_experiment(self):
        if self.record_mode:
            fpath = join(experiment_dir, experiment_recorder_file)
            self.logger.debug(
                "Save experiment {0} [ExperimentRecorder]".format(fpath))
            data = {'eval_method': self.eval_methods.get_method()}
            with open(fpath, 'w') as f:
                dump(data, f, indent=2)
            self.measuring_card.save()
            self.editor.save()

    def save_values(self):
        if self.record_mode:
            self.recorder.save()
    #=========================================================================
    # Methods to load the experiment
    #=========================================================================
    
    def load_experiment(self):
        if self.record_mode:
            with open(join(experiment_dir, experiment_recorder_file), 'r') as f:
                data = load(f)
            self.eval_methods.method.show_value(data["eval_method"])
            self.measuring_card.load()
        self.editor.load()

    def load(self):
        """Load the given phases"""
        self.load_experiment()
        if self.record_mode:
            self.measuring_card.load()
            self.recorder.load(self.measuring_card.input_ports)
        else:
            input_ports = MeasuringCard.load_input_ports()
            self.recorder.load(input_ports)
        self.editor.load()

    def load_components(self):
        self.logger.debug("Load components [ExperimentRecorder]")
        self.load()
        self.correlation_properties.load(
            MeasuringCard.load_input_ports_as_dict())
        
    #=========================================================================
    # Methods to upload the images
    #=========================================================================

    def update_reference(self, f):
        self.recorder.update_reference(f)

    def update_downloaded_preview(self, fpath):
        self.recorder.images.append(fpath)
        i = len(self.recorder.images) - 1
        self.recorder.update_image(i)

    def update_downloaded_image(self, fname):
        self.correlation_properties.correlate(fname)

    def send_image(self):
        """Upload the last recorded image"""
        self.handler.send_image()
    
    #=========================================================================
    # Configuration actions
    #=========================================================================
    
    def configure_measuring_card(self, args):
        try:
            self.measuring_card.update_properties(args)
            return True
        except Exception:
            return False
    #=========================================================================
    # Traitsview
    #=========================================================================

    correlation_properties = Instance(CorrelationProperties)

    type = Instance(ExperimentType)

    started = Bool(False)

    view = View(
        HGroup(
            VGroup(
                VGroup(
                    UItem('editor', style='custom',
                          visible_when="not record_mode"),
                    label='Experiment-Run'
                ),
                VGroup(
                    UItem('correlation_properties', style='custom'),
                    label='Correlation',
                    enabled_when='not started'
                ),
                VGroup(
                    UItem('type', style='custom'),
                    label='Experiment-Type',
                    enabled_when='not started or record_mode'
                ),
                layout='tabbed',
                visible_when="not record_mode"
            ),
            HGroup(
                VGroup(
                    VGroup(
                        UItem('measuring_card', style='custom'),
                        enabled_when="record_mode",
                        label='Card'
                    ),
                    VGroup(
                        VGroup(
                            Item('eval_methods', label="Evaluation:",
                                 enabled_when='not started or not record_mode', style='custom'),
                        ),
                        VGroup(
                            UItem('editor', style='custom'),
                        ),
                        label='Run'
                    ),
                    VGroup(
                        UItem('correlation_properties', style='custom'),
                        label='Correlation',
                        enabled_when='not started'
                    ),
                    VGroup(
                        UItem('type', style='custom'),
                        label='Type',
                        enabled_when='not started'
                    ),
                    layout='tabbed',
                    visible_when="record_mode"
                ),
                VGroup(
                    InstanceUItem('recorder', width=700),
                ),
            ),
            layout='normal'
        )
    )
