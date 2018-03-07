"""
.. module: phases
.. moduleauthor: Marcel Kennert
"""
import warnings
warnings.filterwarnings("ignore")
from time import time, sleep

from UniversalLibrary.UniversalLibrary import UniversalLibraryError
from traits.api import \
    HasTraits, Float, Str, Bool, Int, Button, on_trait_change, Instance
from traitsui.api import View, Item, VGroup, HGroup, spring, UItem, Group
from traitsui.menu import Action, CancelButton

from basic_modules.basic_classes import Combobox
from basic_modules.basic_methods import secs_to_time


class Phase(HasTraits):
    """
    Base class for the phases. Every phase must 
    implement a start-method and belongs a experiment. 
    Optional the phase can have a name for a easy recognizing.
    """

    # Name of the phase. Necessary to recognize the phase
    # in the experiment file
    name = Str

    reset = Bool(True)

    reset_time = Float(0.1)

    started = Bool(False)

    canceled = Bool(False)

    editable = Bool(True)

    record_mode = Bool(False)

    def __init__(self, experiment, name, reset=True, reset_time=0.1):
        """
        :param experiment: Belonging experiment.
        :type experiment: Experiment.
        :param start_value: Interval
        :type start_value: float.
        :param ticks: Increment between the recording.
        :type ticks: float.
        :param name: Name of the phase.
        :type name: str.
        :param reset: True if the trigger should reset after pass the 
                        reset_time, False otherwise. (Default True)
        :type reset: bool.
        :param reset_time: Time to pass until reset the value (in seconds).
        :type reset_time: float.
        """
        if len(name) < 1:
            raise ValueError
        self.model = experiment
        self.record_mode = experiment.record_mode
        self.name = name
        self.reset = reset
        self.reset_time = reset_time

    #=========================================================================
    # Methods to handle the phase
    #=========================================================================

    def start(self):
        """Start the phase."""
        raise NotImplementedError

    def cancel(self):
        """Cancel the phase."""
        self.started = False
        self.canceled = True

    def reset_phase(self):
        """Reset the phase."""
        self.started = False
        self.stopped = False
        self.canceled = False

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
        :rtype: Phase
        """
        raise NotImplementedError

    def save(self):
        """Returns the phase as a dictionary for a JSON file

        :returns: Dictionary with all attributes of the phase
        :rtype: Dictionary
        """
        raise NotImplementedError

    def __str__(self, *args, **kwargs):
        return str(self.__dict__)


class DialogPhase(HasTraits):
    """
    Base class for the dialogs to create a instance of 
    the subclasses of phase. The dialogs should checks all 
    attributes and make sure that a invalid phase can not created.
    """

    error_msg = Str('Make sure the given values are correctly')

    error = Bool(True)

    reset = Bool(True)

    reset_time = Float(0.1)

    model = None

    parent = None
    
    cur_phases=[]
    #=========================================================================
    # Methods to handle the dialog with other classes
    #=========================================================================

    def open_dialog(self):
        """Open the edit dialog"""
        raise NotImplementedError()

    def load(self):
        """
        Create a instance of the class Phase with the attributes
        of the view.

        :returns: Created phase
        :rtype: Phase
        """
        raise NotImplementedError


class PhaseValue(Phase):
    """Represents a phase which is value based."""

    class_name = "PhaseValue"

    id = Int

    start_value = Float

    end_value = Float

    ticks = Float

    def __init__(self, experiment, edit_dialog, start_value, end_value, ticks,
                 port_id, name, reset=True, reset_time=0.1):
        """
        :param experiment: Belonging experiment.
        :type experiment: Experiment
        :param start_value: Start value of the phase.
        :type start_value: float
        :param end_value: End value of the phase.
        :type end_value: float
        :param ticks: Increment between the recording.
        :type ticks: float
        :param port_id: Id of the port which should record.
        :type port_id: int
        :param name: Name of the phase.
        :type name: str
        :param reset: True if the trigger should reset after pass the 
                        reset_time, False otherwise. (Default True)
        :type reset: bool
        :param reset_time: Time to pass until reset the value (in seconds).
        :type reset_time: float
        :raises: UniversalLibraryError
        """
        super(PhaseValue, self).__init__(experiment, name=name,
                                         reset=True, reset_time=0.1)
        if experiment.record_mode and \
                not experiment.measuring_card.input_port_exists(port_id):
            raise UniversalLibraryError(0)
        self.id = port_id
        self.edit_dialog = edit_dialog
        self.start_value = start_value
        self.end_value = end_value
        self.ticks = ticks

    #=========================================================================
    # Methods to handle the phase
    #=========================================================================

    def start(self, first_record=True):
        """Start the phase."""
        self.started = True
        raise_force = self.end_value - self.start_value > 0
        if raise_force:
            self._start_raise(first_record)
        else:
            self._start_decrease(first_record)

    def _start_raise(self, first_record):
        # phase where the force raise
        value = self.model.measuring_card.record_port(self.id)[1]
        uptick = self.start_value if first_record else self.start_value + \
            self.ticks
        while value < self.end_value and not self.canceled:
            value = self.model.measuring_card.record_port(
                self.id)[1]
            if value > uptick:
                uptick += self.ticks
                self.model.use_all_ports(self.reset, self.reset_time)

    def _start_decrease(self, first_record):
        # phase where the force decrease
        value = self.model.measuring_card.record_port(self.id)[1]
        if first_record:
            downtick = self.start_value
        else:
            downtick = self.start_value - self.ticks
        while downtick > self.end_value - self.ticks and not self.canceled:
            value = self.model.measuring_card.record_port(
                self.id)[1]
            if value < downtick:
                downtick -= self.ticks
                self.model.use_all_ports(self.reset, self.reset_time)

    #=========================================================================
    # Methods to save and load the phase
    #=========================================================================

    def save(self):
        """Returns the phase as a dictionary for a JSON file

        :returns: Dictionary with all attributes of the phase
        :rtype: Dictionary
        """
        return {"class_name": self.class_name,
                "name": self.name,
                "reset": self.reset,
                "reset_time": self.reset_time,
                "start_value": self.start_value,
                "end_value": self.end_value,
                "ticks": self.ticks,
                "port_id": self.id
                }

    @staticmethod
    def load(args, experiment):
        """Create a instance with the given attributes

        :param args: Attributes which are saved in the json-file
        :type args: Dictionary
        :param experiment: Related experiment
        :type experiment: ExperimentModel
        :returns: Instance with the loaded attributes
        :rtype: PhaseValue
        """
        if experiment.record_mode:
            edit_dialog = experiment.editor.dialog_value_phase
        else:
            edit_dialog = None
        return PhaseValue(experiment, edit_dialog, args["start_value"],
                          args["end_value"], args["ticks"], args["port_id"],
                          args["name"], args["reset"], args["reset_time"])

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    edit_btn = Button("Edit Phase")

    def _edit_btn_fired(self):
        # not finished yet
        args = [self.start_value, self.end_value, self.ticks, self.id,
                self.name, self.reset, self.reset_time]
        self.edit_dialog._update_attributes(args)
        n = self.parent.get_length_of_phases()
        ports = self.parent.get_ports()
        confirm = self.edit_dialog.open_dialog(n, ports)
        if confirm:
            args = self.edit_dialog._get_attributes()
            self.start_value, self.end_value, self.ticks, self.id,\
                self.name, self.reset, self.reset_time = args
            # not zero based
            pos = self.edit_dialog.position.get_selected_value() - 1
            self.parent.update_phases(self, pos)

    view = View(
        VGroup(
            Item("name", style="readonly"),
            Item("id", label="Port", style="readonly"),
            Item("start_value", style="readonly"),
            Item("end_value", style="readonly"),
            Item("ticks", style="readonly"),
            HGroup(
                spring,
                UItem("edit_btn", visible_when="editable")
            ),
            label="Value-Phase",
            enabled_when="not started and record_mode"
        ),
        resizable=True
    )


class DialogPhaseValue(DialogPhase):
    """
    Dialog to create a instance of the class
    PhaseValue. The dialog checks all attributes and make sure
    that a invalid phase can not created.
    """

    position = Instance(Combobox, ())

    id = Instance(Combobox, ())

    name = Str

    start_value = Float

    end_value = Float

    ticks = Float

    #=========================================================================
    # Methods to handle the dialog with other classes
    #=========================================================================

    def open_dialog(self, phase_num, ports, phases=None):
        if not phases == None:
            self.cur_phases = phases
        self.position.reset()
        self.id.reset()
        for i in range(1, phase_num + 1):
            self.position.add_item("Position " + str(i), i)
        for p in ports:
            self.id.add_item(p.name, p.id)
        self._check_phase()
        return self.configure_traits(kind="livemodal")

    def load(self):
        """Create a instance of the class PhaseValue with the attributes\
            of the view.

        :returns: Value based phase
        :rtype: PhaseValue
        """
        phase = PhaseValue(self.model, self, *self._get_attributes())
        self.name = ""
        return phase

    def _get_attributes(self):
        # Return all attributes of the view.
        pid = self.id.get_selected_value()
        return self.start_value, self.end_value, self.ticks, pid,\
            self.name, self.reset, self.reset_time

    def _update_attributes(self, args):
        # update the attributes of the view
        self.start_value, self.end_value, self.ticks, pid,\
            self.name, self.reset, self.reset_time = args
        self.id.show_value(pid)

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    ConfirmButton = Action(name="OK", enabled_when="not error")

    @on_trait_change("name,id,start_value,end_value,ticks")
    def _check_phase(self):
        # Checks whether the given attributes are correctly.
        try:
            for phase in self.cur_phases:
                if phase.name == self.name:
                    raise ValueError("The name does already exists")
            if self.start_value == self.end_value:
                raise ValueError("The start and end value are the same")
            elif self.ticks <= 0:
                raise ValueError("Ticks must be positve")
            elif self.position < 1:
                raise ValueError("Invalid position")
            PhaseValue(self.model, self, *self._get_attributes())
            self.error = False
        except Exception, e:
            self.error = True
            self.error_msg = str(e)

    view = View(
        Group(
            VGroup(
                Item("position", style="custom"),
                Item("id", label="Port-ID", style="custom"),
                Item("name"),
                Item("start_value"),
                Item("end_value"),
                Item("ticks"),
                Item("reset_time"),
            ),
            Group(
                UItem("error_msg", style="readonly"),
                label="Error:",
                visible_when="error",
                show_border=True,
                style_sheet="*{color:red}"
            ),
            label="Value-Phase"
        ),
        buttons=[ConfirmButton, CancelButton],
        resizable=True,
        width=300,
        height=200,
        title="Create Value-Phase"
    )


class PhaseTime(Phase):
    """Represents a phase which is time based."""

    class_name = "PhaseTime"

    interval = Float

    ticks = Float

    interval_str = Str

    ticks_str = Str

    def __init__(self, experiment, edit_dialog, interval, ticks, name,
                 reset=True, reset_time=0.1, interval_str="", ticks_str=""):
        """
        :param experiment: Belonging experiment.
        :type experiment: Experiment.
        :param edit_dialog: Dialog to edit the phase
        :type edit_dialog: DialogPhaseTime
        :param interval: Time interval in seconds
        :type interval: float.
        :param ticks: Increment between the recording.
        :type ticks: float.
        :param name: Name of the phase.
        :type name: str.
        :param reset: True if the trigger should reset after pass the 
                        reset_time, False otherwise. (Default True)
        :type reset: bool.
        :param reset_time: Time to pass until reset the value (in seconds).
        :type reset_time: float.
        :param interval_str: Interval as string.
        :type interval_str: str.
        :param ticks_str: Ticks as string.
        :type ticks_str: str.
        """
        super(PhaseTime, self).__init__(experiment, name=name,
                                        reset=True, reset_time=0.1)
        self.model = experiment
        self.edit_dialog = edit_dialog
        self.interval = interval
        self.ticks = ticks
        self.interval_str = interval_str
        self.ticks_str = ticks_str

    def start(self):
        """Start the phase."""
        self.started = True
        start_time = time()
        while time() - start_time <= self.interval:
            sleep(self.ticks)
            self.model.use_all_ports(self.reset, self.reset_time)
            if self.canceled:
                return

    #=========================================================================
    # Methods to save and load the phase
    #=========================================================================

    def save(self):
        """Returns the phase as a dictionary for a JSON file

        :returns: Dictionary with all attributes of the phase
        :rtype: Dictionary
        """
        return {"class_name": self.class_name,
                "name": self.name,
                "reset": self.reset,
                "reset_time": self.reset_time,
                "interval": self.interval,
                "interval_str": self.interval_str,
                "ticks": self.ticks,
                "ticks_str": self.ticks_str,
                }

    @staticmethod
    def load(args, experiment):
        """Create a instance with the given attributes

        :param args: Attributes which are saved in the json-file
        :type args: Dictionary
        :param experiment: Related experiment
        :type experiment: ExperimentModel
        :returns: Instance with the loaded attributes
        :rtype: PhaseTime
        """
        if experiment.record_mode:
            edit_dialog = experiment.editor.dialog_time_phase
        else:
            edit_dialog = None
        return PhaseTime(experiment, edit_dialog, args["interval"],
                         args["ticks"], args["name"], args["reset_time"], True,
                         args["interval_str"], args["ticks_str"])

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    edit_btn = Button("Edit Phase")

    def _edit_btn_fired(self):
        # open the edit dialog with the attributes of
        # the selected phase
        args = [self.name, self.reset, self.reset_time,
                self.interval_str, self.ticks_str]
        self.edit_dialog._update_attributes(args)
        n = self.parent.get_length_of_phases()
        confirm = self.edit_dialog.open_dialog(n)
        if confirm:
            self.interval, self.ticks, self.name, self.reset, self.reset_time,\
                self.interval_str, self.ticks_str = self.edit_dialog._get_attributes()
            pos = self.edit_dialog.position.get_selected_value() - 1
            self.parent.update_phases(phase=self, position=pos)

    view = View(
        VGroup(
            Item("interval_str", label="Interval:", style="readonly"),
            Item("ticks_str", label="Ticks:", style="readonly"),
            Item("reset", style="readonly"),
            Item("reset_time", style="readonly"),
            HGroup(
                spring,
                UItem("edit_btn", visible_when="editable")
            ),
            label="Time-Phase",
            enabled_when="not started"
        ),
        resizable=True,
    )


class DialogPhaseTime(DialogPhase):
    """
    Dialog to create a instance of the class
    PhaseTime. The dialog checks all attributes and make sure
    that a invalid phase can not created.
    """

    position = Instance(Combobox, ())

    name = Str

    interval = Str(secs_to_time(0))

    ticks = Str(secs_to_time(0))

    def _get_attributes(self):
        # Return all attributes of the view.
        idays, ihours, imins, isecs = map(int, self.interval.split(":"))
        interval = idays * 24 * 60**2 + ihours * 60**2 + imins * 60 + isecs
        tdays, thours, tmins, tsecs = map(int, self.ticks.split(":"))
        ticks = tdays * 24 * 60**2 + thours * 60**2 + tmins * 60 + tsecs
        return interval, ticks, self.name, self.reset, self.reset_time,\
            self.interval, self.ticks

    def _update_attributes(self, args):
        # update the attributes of the view with the given arguments
        self.name, self.reset, self.reset_time,\
            self.interval, self.ticks = args

    #=========================================================================
    # Methods to handle the dialog with other classes
    #=========================================================================

    def open_dialog(self, phase_num, phases=None):
        if not phases == None:
            self.cur_phases = phases
        self.position.reset()
        for i in range(1, phase_num + 1):
            self.position.add_item("Position " + str(i), i)
        self._check_attributes()
        return self.configure_traits(kind="livemodal")

    def load(self):
        """Create a instance of the class PhaseTime with the attributes\
            of the view.

        :returns: Time based phase
        :rtype: PhaseTime
        """
        phase = PhaseTime(self.model, self, *self._get_attributes())
        self.name = ""
        return phase

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    ConfirmButton = Action(name="OK", enabled_when="not error")

    @on_trait_change("name,interval,ticks")
    def _check_attributes(self):
        # Checks whether the given attributes are correctly.
        try:
            for phase in self.cur_phases:
                if phase.name == self.name:
                    raise ValueError("The name does already exists")
            interval, ticks = self._get_attributes()[:2]
            if interval < 1:
                raise ValueError("The interval must be positive")
            elif ticks < 1:
                raise ValueError("The ticks must be positive")
            elif ticks > interval:
                raise ValueError("The interval must be greater than the ticks")
            elif self.position.get_selected_value() < 1:
                raise ValueError("The position is invalid")
            PhaseTime(self.model, None, *self._get_attributes())
            self.error = False
        except Exception, e:
            self.error = True
            self.error_msg = str(e)

    view = View(
        Group(
            VGroup(
                Item("position", style="custom"),
                Item("name"),
                Item("reset_time"),
                Item("interval", label="Interval (d:h:m:s):"),
                Item("ticks", label="Ticks (d:h:m:s):"),
                label="General"
            ),
            Group(
                UItem("error_msg", style="readonly"),
                label="Error:",
                visible_when="error",
                show_border=True,
                style_sheet="*{color:red}"
            ),
            layout="normal"
        ),
        title="Create Time-Phases",
        buttons=[ConfirmButton, CancelButton],
        resizable=True
    )


class PhasePause(Phase):
    """Represents a phase which does not recordings."""

    class_name = "PhasePause"

    limit = Float()

    smaller = Bool()

    time = Int()

    def __init__(self, experiment, edit_dialog, limit, smaller, time,
                 port_id, name, reset=True, reset_time=0.1):
        super(PhasePause, self).__init__(experiment, name=name,
                                         reset=True, reset_time=0.1)
        if experiment.record_mode and \
                not experiment.measuring_card.input_port_exists(port_id):
            raise ValueError("The given port does not exist")
        self.id = port_id
        self.edit_dialog = edit_dialog
        self.smaller = smaller
        self.limit = limit
        self.time = time

    #=========================================================================
    # Methods to save and load the phase
    #=========================================================================

    def start(self):
        """Start the phase."""
        self.started = True
        self.counter = 0
        while not self.canceled:
            value = self.model.measuring_card.record_port(self.id)[1]
            if self.smaller:
                if value < self.limit:
                    self.counter += 1
                    sleep(1)
                else:
                    self.counter = 0
            else:
                if value > self.limit:
                    self.counter += 1
                    sleep(1)
                else:
                    self.counter = 0
            if self.counter >= self.time:
                break

    #=========================================================================
    # Methods to save and load the phase
    #=========================================================================

    def save(self):
        """Returns the phase as a dictionary for a JSON file

        :returns: Dictionary with all attributes of the phase
        :rtype: Dictionary
        """
        return {'class_name': self.class_name,
                'name': self.name,
                'reset': self.reset,
                'reset_time': self.reset_time,
                'limit': self.limit,
                'smaller': self.smaller,
                'time': self.time,
                'port_id': self.id
                }

    @staticmethod
    def load(args, experiment):
        """Create a instance with the given attributes

        :param args: Attributes which are saved in the json-file
        :type args: Dictionary
        :param experiment: Related experiment
        :type experiment: ExperimentModel
        :returns: Instance with the loaded attributes
        :rtype: PhaseValue
        """
        if experiment.record_mode:
            edit_dialog = experiment.editor.dialog_inter_phase
        else:
            edit_dialog = None
        return PhasePause(experiment, edit_dialog, args['limit'],
                          args['smaller'], args['time'], args['port_id'],
                          args['name'], args['reset'], args['reset_time'])
    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    edit_btn = Button('Edit Phase')

    def _edit_btn_fired(self):
        # not finished yet
        args = [self.limit, self.smaller, self.time, self.id,
                self.name, self.reset, self.reset_time]
        self.edit_dialog._update_attributes(args)
        n = self.parent.get_length_of_phases()
        ports = self.parent.get_ports()
        confirm = self.edit_dialog.open_dialog(n, ports)
        if confirm:
            args = self.edit_dialog._get_attributes()
            self.limit, self.smaller, self.time, self.id,\
                self.name, self.reset, self.reset_time = args
            # not zero based
            pos = self.edit_dialog.position.get_selected_value() - 1
            self.parent.update_phases(self, pos)

    view = View(
        VGroup(
            Item('name', style='readonly'),
            Item('id', label='Port', style='readonly'),
            Item('limit', style='readonly'),
            Item('time', label='Time [s]:',  style='readonly'),
            Item('smaller',  style='readonly'),
            HGroup(
                spring,
                UItem('edit_btn', visible_when='editable')
            ),
            label='Interphase',
            enabled_when='not started'
        )
    )


class DialogPhaseInter(DialogPhase):

    position = Instance(Combobox, ())

    id = Instance(Combobox, ())

    name = Str

    limit = Float

    smaller = Bool

    time = Int

    #=========================================================================
    # Methods to handle the dialog with other classes
    #=========================================================================

    def open_dialog(self, phase_num, ports, phases=None):
        if not phases == None:
            self.cur_phases = phases
        self.position.reset()
        self.id.reset()
        for i in range(1, phase_num + 1):
            self.position.add_item('Position ' + str(i), i)
        for p in ports:
            self.id.add_item(p.name, p.id)
        self._check_phase()
        return self.configure_traits(kind='livemodal')

    def load(self):
        """Create a instance of the class PhaseValue with the attributes\
            of the view.

        :returns: Value based phase
        :rtype: PhaseValue
        """
        phase = PhasePause(self.model, self, *self._get_attributes())
        self.name = ''
        return phase

    def _get_attributes(self):
        # Return all attributes of the view.
        pid = self.id.get_selected_value()
        return self.limit, self.smaller, self.time, pid,\
            self.name, self.reset, self.reset_time

    def _update_attributes(self, args):
        # update the attributes of the view
        self.limit, self.smaller, self.time, pid,\
            self.name, self.reset, self.reset_time = args
        self.id.show_value(pid)

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    ConfirmButton = Action(name='OK', enabled_when='not error')

    @on_trait_change('name,id,time,limit')
    def _check_phase(self):
        # Checks whether the given attributes are correctly.
        try:
            for phase in self.cur_phases:
                if phase.name == self.name:
                    raise ValueError("The name does already exists")
            if self.time < 1:
                raise ValueError('The time must positive')
            PhasePause(self.model, self, *self._get_attributes())
            self.error = False
        except Exception, e:
            self.error = True
            self.error_msg = str(e)

    view = View(
        Group(
            VGroup(
                Item('position', style='custom'),
                Item('id', label='Port-ID', style='custom'),
                Item('name'),
                Item('limit'),
                Item('time'),
                Item('smaller'),
            ),
            Group(
                UItem('error_msg', style='readonly'),
                label='Error:',
                visible_when='error',
                show_border=True,
                style_sheet='*{color:red}'
            ),
            label='Inter-Phase'
        ),
        buttons=[ConfirmButton, CancelButton],
        resizable=True,
        width=300,
        height=200,
        title='Create Value-Phase'
    )
