"""
.. module: phase_container
.. moduleauthor: Marcel Kennert
"""
from copy import deepcopy
from json import load, dump
from logging import getLogger
from os.path import join
import warnings

from traits.api import \
    Int, Str, Instance, Button, List, HasTraits, Bool
from traitsui.api import View, Item,  VGroup, ListEditor, UItem, HGroup, spring
from traitsui.menu import Action, CancelButton

from application.configuration import experiment_dir, phases_file
from basic_modules.basic_classes import Combobox
from experiment.recorder.phase_editor.phases import \
    Phase, PhaseValue, DialogPhase, PhaseTime,\
    PhasePause, DialogPhaseTime, DialogPhaseValue, DialogPhaseInter


warnings.filterwarnings("ignore")


class IPhaseContainer(object):
    """Base class for objects which contains all phases"""

    logger = getLogger('Application')

    model = None

    phases = List(Phase)

    add_btn = Button('Add')

    all_phases = [PhaseValue, PhaseTime, PhasePause]

    #=========================================================================
    # Define all phase dialogs
    #=========================================================================

    dialog_time_phase = DialogPhaseTime()

    dialog_value_phase = DialogPhaseValue()

    dialog_inter_phase = DialogPhaseInter()

    dialogs = [dialog_time_phase, dialog_value_phase, dialog_inter_phase]

    def __init__(self):
        #======================================================================
        # Add dialogs to the combobox
        #======================================================================
        self.combobox.add_item('Time-Phase', self._add_time_phase)
        self.combobox.add_item('Value-Phase', self._add_value_phase)
        self.combobox.add_item('Cycle', self._add_cycle)
        self.combobox.add_item('Inter-Phase', self._add_inter_phase)
        self.imported_independent_modules = False

    #=========================================================================
    # Define how the dialog should open
    #=========================================================================

    def load_phase(self, class_name, args, model):
        if not self.imported_independent_modules:
            self.imported_independent_modules
        return IPhaseContainer._load_phase(class_name, args, model)

    @staticmethod
    def _load_phase(class_name, args, model):
        for phase in IPhaseContainer.all_phases:
            if phase.class_name == class_name:
                return phase.load(args, model)

    def _add_btn_fired(self):
        self.combobox.get_selected_value()()

    def _add_inter_phase(self):
        self.__open_dialog(self.dialog_inter_phase, ports=True)

    def _add_value_phase(self):
        self.__open_dialog(self.dialog_value_phase, ports=True)

    def _add_time_phase(self):
        self.__open_dialog(self.dialog_time_phase)

    def _add_cycle(self):
        if not self.imported_independent_modules:
            self.import_dependent_modules()
        self.__open_dialog(self.dialog_cyle)

    def import_dependent_modules(self):
        from experiment.recorder.phase_editor.phase_container \
            import Cycle, DialogCycle
        self.imported_independent_modules = True
        self.all_phases.append(Cycle)
        self.dialog_cyle = DialogCycle()
        self.dialog_cyle.model = self.model
        self.dialog_cyle.parent = self
        self.dialogs.append(self.dialog_cyle)

    def __open_dialog(self, dialog, ports=False):
        # open a dialog to create a new
        # time phase for the experiment
        if ports:
            ports = self.model.measuring_card.input_ports
            confirm = dialog.open_dialog(
                len(self.phases) + 1, ports, self.phases)
        else:
            confirm = dialog.open_dialog(len(self.phases) + 1, self.phases)
        if confirm:
            pos = dialog.position.get_selected_value() - 1
            phase = dialog.load()
            phase.parent = self
            self.phases.insert(pos, phase)
            self._update_phases()

    #=========================================================================
    # Important functions for the container
    #=========================================================================

    def update_phases(self, phase, position):
        self.phases.remove(phase)
        self.phases.insert(position, phase)
        self._update_phases()

    def _update_phases(self):
        # update the list with the right position
        self.logger.debug("Update all phases")
        phases = deepcopy(self.phases)
        del self.phases[:]
        for phase in phases:
            self.logger.debug("\t" + str(phase))
            self.phases.append(phase)

    def set_model(self, experiment):
        self.model = experiment
        for dialog in self.dialogs:
            dialog.model = experiment
            dialog.parent = self

    def get_ports(self):
        return self.model.measuring_card.input_ports

    def get_length_of_phases(self):
        return len(self.phases)


class Cycle(Phase):
    """Represents a cycle which consists phases and can repeated."""

    class_name = Str('Cycle')

    phases = List

    repeats = Int

    def __init__(self, experiment, edit_dialog, name, phases, repeats):
        super(Cycle, self).__init__(experiment, name)
        self.edit_dialog = edit_dialog
        self.phases = phases
        self.repeats = repeats
        for phase in self.phases:
            phase.parent = self

    #=========================================================================
    # Methods to handle the phase
    #=========================================================================

    def start(self):
        """Start the phase."""
        self.started = True
        value = self.repeats
        end_value = None
        n = len(self.phases)
        while value > 0:
            for i in range(n):
                phase = self.phases[i]
                if isinstance(phase, PhaseValue):
                    if end_value == phase.start_value and i < n - 1:
                        phase.start(False)
                    else:
                        phase.start()
                    end_value = phase.end_value
                else:
                    phase.start()
            value -= 1

    def cancel(self):
        """Cancel the phase."""
        for phase in self.phases:
            phase.cancel()

    def reset_phase(self):
        """Reset all phases of the cycle."""
        for phase in self.phases:
            phase.reset_phase()
        self.started = False

    def get_ports(self):
        return self.parent.get_ports()

    def get_length_of_phases(self):
        return len(self.phases)

    #=========================================================================
    # Methods to save and load the phase
    #=========================================================================

    @staticmethod
    def load(args, experiment):
        """Create a instance with the given attributes

        :param args: Attributes which are saved in the json-file
        :type args: Dictionary
        :param experiment: Related experiment
        :type experiment: ExperimentModel
        :returns: Instance with the loaded attributes
        :rtype: Cycle
        """
        if experiment.record_mode:
            edit_dialog = experiment.editor.dialog_cyle
        else:
            edit_dialog = None
        phases = args["phases"]
        cur_phases = []
        for args in phases:
            class_name = args["class_name"]
            phase = IPhaseContainer._load_phase(class_name, args, experiment)
            phase = getattr(globals()[str(class_name)], "load")(
                args, experiment)
            cur_phases.append(phase)
        return Cycle(experiment, edit_dialog, args["name"],
                     cur_phases, args["repeats"])

    def save(self):
        """Returns the phase as a dictionary for a JSON file

        :returns: Dictionary with all attributes of the phase
        :rtype: Dictionary
        """
        data = {}
        data["class_name"] = self.class_name
        data["name"] = self.name
        data["repeats"] = self.repeats
        data["phases"] = []
        for phase in self.phases:
            data["phases"].append(phase.save())
        return data

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    edit_btn = Button("Edit Phase")

    def _edit_btn_fired(self):
        # open a dialog to edit the cycle
        args = [self.name, self.phases, self.repeats]
        self.edit_dialog._update_attributes(args)
        for phase in self.phases:
            phase.editable = True
        confirm = self.edit_dialog.open_dialog(len(self.parent.phases))
        if confirm:
            args = self.edit_dialog._get_attributes()
            self.name, self.phases, self.repeats = args
        for phase in self.phases:
            phase.editable = False

    view = View(
        VGroup(
            VGroup(
                Item("name", style="readonly"),
                Item("repeats", style="readonly"),
                label="Cycle",
            ),
            UItem("phases", style="custom",
                  editor=ListEditor(use_notebook=True, deletable=True,
                                    page_name=".name")
                  ),
            HGroup(
                spring,
                UItem("edit_btn")
            ),
            enabled_when="not started"
        )
    )


class DialogCycle(DialogPhase, IPhaseContainer):
    """
    Dialog to create a instance of the class
    Cycle. The dialog checks all attributes and make sure
    that a invalid cycle can not created.
    """

    position = Instance(Combobox, ())

    name = Str

    phases = List()

    repeats = Int

    def __init__(self):
        IPhaseContainer.__init__(self)
        self.logger.debug("Initialize cycle")

    #=========================================================================
    # Methods to handle the dialog with other classes
    #=========================================================================

    def open_dialog(self, phase_num, phases):
        self.cur_phases = phases
        self.position.reset()
        for i in range(1, phase_num + 1):
            self.position.add_item("Position " + str(i), i)
        return self.configure_traits(kind="livemodal")

    def load(self):
        """Create a instance of the class Cycle with the attributes\
            of the view.

        :returns: Created cycle
        :rtype: Cycle
        """
        cycle = Cycle(self.model, self, *self._get_attributes())
        self.name = ""
        self.phases = []
        self.invalid_phase = True
        return cycle

    def _update_attributes(self, args):
        # update the view with the given attributes
        self.name, self.phases, self.repeats = args

    def _get_attributes(self):
        # Return all attributes of the view.
        return self.name, self.phases, self.repeats

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    combobox = Instance(Combobox, ())

    ConfirmButton = Action(name="OK", enabled_when="not error")

    add_btn = Button('Add')

    def _name_changed(self):
        try:
            for phase in self.cur_phases:
                if phase.name == self.name:
                    raise ValueError("The name does already exists")
            if len(self.name) < 1:
                raise ValueError("Define a name for the phase")
            self.error = False
        except Exception, e:
            self.error = True
            self.error_msg = str(e)

    def repeats_changed(self):
        try:
            if self.repeats < 1:
                raise ValueError("The repeats must bigger than 0")
            self.error = False
        except Exception, e:
            self.error = True
            self.error_msg = str(e)

    def phases_changed(self):
        if len(self.phases) < 1:
            raise ValueError("Define a phases")
        self.error = False

    view = View(
        VGroup(
            Item("position", style="custom"),
            Item("phases", style="custom",
                 editor=ListEditor(use_notebook=True, deletable=True,
                                   page_name=".name")
                 ),
            VGroup(
                HGroup(
                    UItem('combobox', style='custom'),
                    UItem('add_btn'),
                ),
            ),
            Item("name"),
            Item("repeats"),
            VGroup(
                UItem("error_msg", style="readonly"),
                label="Error:",
                visible_when="error",
                show_border=True,
                style_sheet="*{color:red}"
            ),
            label="Cycle"
        ),
        buttons=[ConfirmButton, CancelButton],
        resizable=True,
        width=300,
        height=200,
        title="Create Cycle"
    )


class PhaseEditor(HasTraits, IPhaseContainer):
    """Editor to manage the phases of the experiment."""

    phases = List(Phase)

    combobox = Instance(Combobox, ())

    logger = getLogger('Application')

    record_mode = Bool()

    def __init__(self, record_mode):
        IPhaseContainer.__init__(self)
        self.logger.debug('Initialize PhaseEditor')
        self.record_mode = record_mode

    def is_valid(self):
        if len(self.phases) < 1:
            raise ValueError("Define a phase")

    #=========================================================================
    # Methods to handle the phases
    #=========================================================================

    def _cancel_record(self):
        # cancel the whole record-process
        for phase in self.phases:
            phase.cancel()

    def _reset_phases(self):
        # reset all running time attributes
        # to default
        for phase in self.phases:
            phase.reset_phase()

    #=========================================================================
    # Methods to save and load the phases
    #=========================================================================

    def save(self):
        """Save the phases as a json-directory"""
        fpath = join(experiment_dir, phases_file)
        self.logger.debug("Save phases {0} [PhaseEditor]".format(fpath))
        data = {}
        data['phases'] = []
        for phase in self.phases:
            data['phases'].append(phase.save())
        with open(fpath, 'w') as f:
            dump(data, f, indent=2)

    def load(self):
        """Load the given phases

        :param phases: Phases
        :type phases: List()
        """
        del self.phases[:]
        with open(join(experiment_dir, phases_file), 'r') as f:
            data = load(f)
        phases = data['phases']
        for args in phases:
            class_name = args['class_name']
            phase = self.load_phase(class_name, args, self.model)
            self.phases.append(phase)
            phase.parent = self
            phase.model = self.model

    @staticmethod
    def generate_phases():
        fpath = join(experiment_dir, phases_file)
        data = {}
        data['phases'] = []
        with open(fpath, 'w') as f:
            dump(data, f, indent=2)
    #=========================================================================
    # Traitsview
    #=========================================================================

    add_btn = Button('Add')

    traits_view = View(
        VGroup(
            UItem('phases', style='custom',
                  editor=ListEditor(use_notebook=True, deletable=True,
                                    page_name='.name'),
                  ),
            VGroup(
                HGroup(
                    UItem('combobox', style='custom'),
                    UItem('add_btn'),
                    visible_when="record_mode"
                ),
            ),
            label='Phases'
        ),
    )
