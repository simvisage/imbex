"""
.. module: methods
.. moduleauthor: Marcel Kennert
"""
from logging import getLogger

from traits.api import HasTraits, Instance
from traitsui.api import View, UItem

from basic_modules.basic_classes import RunThread, Combobox


logger = getLogger("Application")

#=========================================================================
# Methods to record the experiment
#=========================================================================


def evaluate_live(model):
    # not in use
    for phase in model.editor.phases:
        logger.debug("Start phase {0} [ExperimentModel]".format(phase))
        model.handler.update_phase(phase.name)
        phase.start()
        RunThread(target=model.send_image)


def evaluate_after_experiment(model):
    for phase in model.editor.phases:
        logger.debug("Start phase {0} [ExperimentModel]".format(phase))
        model.handler.update_phase(phase.name)
        phase.start()

#=========================================================================
# Class to use the recording-methods
#=========================================================================


class EvalMethods(HasTraits):

    """
    Provides methods which determine how the experiment
    will recorded and evaluate.
    """

    method = Instance(Combobox, ())

    def __init__(self, model):
        self.model = model
        self.method.add_item('After Experiment', evaluate_after_experiment)

    def evaluate(self, model):
        """Record and evaluate the model.

        :param model: Model of the experiment
        :type model: ExperimentModel
        """
        self.log_informations(model)
        logger.debug("Start recording [EvalMethods]")
        model.started = model.measuring_card.started = True
        method = self.method.get_selected_value()
        logger.debug("Evaluation-type: " + self.method.selected_key)
        method(model)
        logger.debug("Experiment is finished [EvalMethods]")
        model.editor._reset_phases()
        model.handler._finished_experiment()
        model.started = model.measuring_card.started = False

    def log_informations(self, model):
        """Logged all ports and attributes of the model.

        :param model: Model of the experiment
        :type model: ExperimentModel
        """
        logger.debug("The following ports are registered")
        for port in model.measuring_card.get_all_ports():
            logger.debug("Port: {0}".format(port))
        logger.debug("The following phases are registered")
        for phase in model.editor.phases:
            logger.debug("Phase: {0}".format(phase))

    def get_method(self):
        return self.method.selected_key

    #=========================================================================
    # Traitsview
    #=========================================================================
    view = View(
        UItem('method', style='custom')
    )
