"""
.. module: ports
.. moduleauthor: Marcel Kennert
"""
from time import sleep

from traits.api import \
    HasTraits, Int, Str, Bool, Instance, Float, Button, on_trait_change
from traitsui.api import View, Item, VGroup, HGroup, spring, UItem, Group
from traitsui.menu import Action, CancelButton

import UniversalLibrary as UL
from basic_modules.basic_classes import Combobox, RunThread


class Port(HasTraits):
    """
    Base class for the ports. Every port must have a id , the id
    of the measuring card and know whether it is a input-port.
    """

    id = Int()

    name = Str()

    is_input_port = Bool()

    def __init__(self, board, port_id, name):
        if len(name) < 1:
            raise ValueError("Enter a name")
        self.board, self.id, self.name = board, port_id, name

    #=========================================================================
    # Methods to save and load the port
    #=========================================================================

    def save(self):
        """Returns the port as a dictionary for a JSON file

        :returns: Dictionary with all attributes of the port
        :rtype: Dictionary
        """
        raise NotImplementedError()

    @staticmethod
    def load(args, card):
        """Creates a instance with the given attributes

        :param args: Attributes which are saved in the json-file
        :type args: Dictionary
        :param card: Measuring card of the experiment
        :type card: MeasuringCard
        :returns: Instance with the loaded attributes
        :rtype: Port
        """
        raise NotImplementedError()

    def __str__(self, *args, **kwargs):
        return "Port-Attributes:" + str(self.__dict__)


class DialogPort(HasTraits):
    """
    Base class for the dialogs to create a instance of 
    the subclasses of port. The dialogs should checks all 
    attributes and make sure that a invalid port can not created.
    """

    id = Instance(Combobox, ())

    error_msg = Str()

    error = Bool(True)

    #=========================================================================
    # Methods to handle the dialog with other classes
    #=========================================================================

    def open_dialog(self):
        """Open the dialog to input the values for the port.

        :returns: True, if the user want create a port, False otherwise
        :rtype: bool
        """
        raise NotImplementedError()

    def load(self):
        """
        Creates a instance of the class Por with the attributes
        of the view.

        :returns: Port
        """
        raise NotImplementedError()


class InputPort(Port):
    """Base-class for the input ports."""

    is_input_port = Bool(True)

    #=========================================================================
    # Methods to handle the port
    #=========================================================================

    def record_port(self, volt_interval):
        """
        Reads in the electrical voltage and transforms \
        the value with the scale factor and the offset.

        :param volt_interval: Interval of the electrical voltage of the machine
        :type volt_interval: int
        :return: The value of the machine
        :rtype: float
        :raises: ValueError
        """
        raise ValueError("This is not a input port!")


class OutputPort(Port):
    """Base-class for the output ports."""

    is_input_port = Bool(False)

    def trigger(self, value):
        """Triggers a signal.

        :param value: Volt value in bits (0-255) 
        :type value: int
        :returns: True if the signal was sent, False otherwise
        :rtype: bool
        :raises: ValueError, ctypes.ArgumentError
        """
        raise ValueError("This is not a output port!")


class PortAI(InputPort):
    """
    PortAI represents a analog input port. The class 
    provide a method to read the analog input of the port 
    and transform the value with the given scale-factor and the offset
    """

    scale_factor = Float

    offset = Float

    def __init__(self, board, port_id, scale_factor,
                 offset, name, edit_dialog=None):
        super(PortAI, self).__init__(board, port_id, name)
        if scale_factor == 0:
            raise ValueError("The scalefactor must unequal 0")
        self.scale_factor = scale_factor
        self.offset = offset
        self.edit_dialog = edit_dialog

    #=========================================================================
    # Methods to handle the port
    #=========================================================================

    def record_port(self, volt_interval=UL.BIP10VOLTS):
        """Reads the electrical voltage and transforms \
           the value with the scale factor and the offset.

        :param volt_interval: Interval of the electrical voltage of the machine
        :type volt_interval: int.
        :returns: The value of the machine
        :rtype: float
        """
        data = UL.cbAIn(self.board.id, self.id, volt_interval)
        volt = UL.cbToEngUnits(self.board.id, volt_interval, data)
        return self.scale_factor * volt + self.offset

    #=========================================================================
    # Methods to save and load the port
    #=========================================================================

    def save(self):
        """Returns the port as a dictionary for a JSON file

        :returns: Dictionary with all attributes of the port
        :rtype: Dictionary
        """
        return {"class_name": "PortAI", "name": self.name,
                "id": self.id, "input": self.is_input_port,
                "scale": self.scale_factor, "offset": self.offset}

    @staticmethod
    def load(args, card):
        """Creates a instance with the given attributes

        :param args: Attributes which are saved in the json-file
        :type args: Dictionary
        :param card: Measuring card of the experiment
        :type card: MeasuringCard
        :returns: Instance with the given attributes
        :rtype: PortAI
        """
        if card == None:
            edit_dialog = None
        else:
            edit_dialog = card.dialog_portai
        return PortAI(card, args["id"], args["scale"], args["offset"],
                      args["name"], edit_dialog)

    @staticmethod
    def generate_file(pid, name):
        return {"class_name": "PortAI", "name": name,
                "id": pid, "input": True, "scale": 1, "offset": 0}
    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    edit_btn = Button("Edit Port")

    def _edit_btn_fired(self):
        # edit the port
        self.board.input_ports.remove(self)
        args = [self.id, self.scale_factor, self.offset, self.name]
        self.edit_dialog.update_attributes(args)
        if self.edit_dialog.open_dialog():
            self.board, self.id, self.scale_factor, \
                self.offset, self.name = self.edit_dialog._get_attributes()
        self.board.input_ports.append(self)

    traits_view = View(
        VGroup(
            Item("id", label="Port-ID", style="readonly"),
            Item("scale_factor", label="Scale", style="readonly"),
            Item("offset", style="readonly"),
            HGroup(
                spring,
                UItem("edit_btn")
            )
        ),
        resizable=True
    )


class DialogPortAI(DialogPort):
    """
    Dialog to create a instance of the class
    PortAI. The dialog checks all attributes and make sure
    that a invalid port can not created.
    """

    name = Str()

    scale_factor = Float()

    offset = Float()

    value = Float()

    update_running = Bool(False)

    ConfirmButton = Action(name="OK", enabled_when="not error")

    def __init__(self, measuring_card):
        self.measuring_card = measuring_card
        for i in range(8):
            self.id.add_item("Input {0}".format(i), i)

    #=========================================================================
    # Methods to handle the dialog with other classes
    #=========================================================================

    def open_dialog(self):
        """Open the dialog to input the values for the port.

        :returns: True, if the user want create a port, False otherwise
        :rtype: bool
        """
        self.update_running = True
        # updates the value of the port automatically after pass a given time
        # to make sure that the user see all of the time
        # the current value of the port
        RunThread(target=self._update_value)
        self._check_attributes()
        confirm = self.configure_traits(kind="livemodal")
        self.update_running = False
        return confirm

    def load(self):
        """Creates a instance of the class PortAI with the attributes\
            of the view.

        :returns: Analog input port with the attributes.
        :rtype: PortAI
        """
        port = PortAI(self.measuring_card, self.id.get_selected_value(),
                      self.scale_factor, self.offset, self.name, self)
        # resets the name and set the invalid port to true
        # to make sure that the new port will be checked
        self.name = ""
        self.invalid_port = True
        return port

    def update_attributes(self, args):
        # update the view with the arguments of the port
        pid, self.scale_factor, self.offset, self.name = args
        self.id.show_value(pid)

    def _update_value(self):
        # Update the value to show the current recorded value
        # of the port.
        while self.update_running:
            sleep(0.2)
            self._check_attributes()

    def _get_attributes(self):
        # return all attributes of the view
        return self.measuring_card, self.id.get_selected_value(), \
            self.scale_factor, self.offset, self.name

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    @on_trait_change("scale_factor,offset,board_id,port_id,name")
    def _check_attributes(self):
        # Checks whether the given attributes are correctly and no port
        # with the same id already exist
        try:
            port = PortAI(self.measuring_card, self.id.get_selected_value(),
                          self.scale_factor, self.offset, self.name, None)
            self.value = port.record_port(self.measuring_card.volt_interval)
            if self.measuring_card.input_port_exists(self.id.get_selected_value()):
                raise ValueError("The selected port is already in use")
            self.error = False
        except ValueError, e:
            self.value = 0
            self.error = True
            self.error_msg = str(e)

    analog_input_view = View(
        VGroup(
            Item("id", label="Port-ID", style="custom"),
            Item("name", label="Name [Unit]"),
            Item("scale_factor"),
            Item("offset"),
            Item("value", style="readonly"),
            Group(
                UItem("error_msg", style="readonly"),
                visible_when="error",
                show_border=True,
                label="Error:",
                style_sheet="*{color:red}"
            ),
            label="Input-Port"
        ),
        resizable=True,
        buttons=[ConfirmButton, CancelButton],
        title="Add Input Port",
        width=300,
        height=200,
    )


class PortDO(OutputPort):
    """
    PortDO represents a digital output port. The class 
    provide a method to trigger a digital signal.
    """

    def __init__(self, board, port_id, name, edit_dialog):
        super(PortDO, self).__init__(board, port_id, name)
        self.edit_dialog = edit_dialog
        self.value = 0
        UL.cbDConfigPort(board.id, self.id, UL.DIGITALOUT)
        UL.cbDOut(self.board.id, self.id, self.value)

    #=========================================================================
    # Methods to handle the port
    #=========================================================================

    def trigger(self, reset_time=-1):
        """Triggers a digital signal.

        :param reset_time: Time (in seconds) to pass until reset the value. \
            If the reset_time will not set, the trigger will change \
            the electrical voltage.
        :type reset_time: float.
        :returns: True if the signal was sent, False otherwise.
        :rtype: bool
        :raises: ValueError, ctypes.ArgumentError
        """
        if reset_time < -1:
            raise ValueError("Invalid value: Value must positive")
        value = 0 if self.value == 255 else 255
        if reset_time != -1:
            UL.cbDOut(self.board.id, self.id, value)
            sleep(reset_time)
            UL.cbDOut(self.board.id, self.id, self.value)
        else:
            UL.cbDOut(self.board.id, self.id, value)
            self.value = value
        return True

    #=========================================================================
    # Methods to save and load the port
    #=========================================================================

    def save(self):
        """Returns the port as a dictionary for a JSON file

        :returns: Dictionary with all attributes of the port
        :rtype: Dictionary
        """
        return {"class_name": "PortDO", "name": self.name,
                "id": self.id, "input": self.is_input_port}

    @staticmethod
    def load(args, card):
        """Creates a instance with the given attributes

        :param args: Attributes which are saved in the json-file
        :type args: Dictionary
        :param card: Measuring card of the experiment
        :type card: MeasuringCard
        :returns: Instance with the loaded attributes
        :rtype: PortDO
        """
        edit_dialog = card.dialog_portdo
        return PortDO(card, args["id"], args["name"], edit_dialog)

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    edit_btn = Button("Edit Port")

    def _edit_btn_fired(self):
        # edit the port
        self.board.output_ports.remove(self)
        if self.edit_dialog.open_dialog():
            self.board, self.id, self.name = self.edit_dialog._get_attributes()
        self.board.output_ports.append(self)

    traits_view = View(
        VGroup(
            Item("id", label="Port-ID", style="readonly"),
            Item("name", style="readonly"),
            HGroup(
                spring,
                UItem("edit_btn")
            )
        ),
        resizable=True
    )


class DialogPortDO(DialogPort):
    """
    Dialog to create a instance of the class
    PortDO. The dialog checks all attributes and make sure
    that a invalid port can not created.
    """

    def __init__(self, measuring_card):
        self.measuring_card = measuring_card
        self.id.add_item("Auxport", UL.AUXPORT)

    #=========================================================================
    # Methods to handle the dialog with other classes
    #=========================================================================

    def open_dialog(self):
        """Open the dialog to input the values for the port.

        :returns: True, if the user want create a port, False otherwise
        :rtype: bool
        """
        self._check_attributes()
        return self.configure_traits(kind="livemodal")

    def load(self):
        """Creates a instance of the class PortAI with the attributes \
            of the view.

        :returns: Digital output port with the attributes.
        :rtype: PortDO
        """
        port = PortDO(self.measuring_card, self.id.get_selected_value(),
                      self.id.selected_key, self)
        # resets the name and set the invalid port to true
        # to make sure that the new port will be checked
        self.name = ""
        self.error = True
        return port

    def _get_attributes(self):
        # return all attributes of the view
        pid = self.id.get_selected_value()
        return self.measuring_card, pid, self.id.selected_key

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    ConfirmButton = Action(name="OK", enabled_when="not error")

    @on_trait_change("board_id,port_id,name")
    def _check_attributes(self):
        # Checks whether the given attributes are correctly and no port
        # with the same id already exist
        try:
            PortDO(self.measuring_card, self.id.get_selected_value(),
                   self.id.selected_key, None)
            pid = self.id.get_selected_value()
            if self.measuring_card.output_port_exists(pid):
                raise ValueError("The port is already in use")
            self.error = False
        except ValueError, e:
            self.error_msg = str(e)
            self.error = True

    view = View(
        VGroup(
            Item("id", label="Port-ID", style="custom"),
            Group(
                UItem("error_msg", style="readonly"),
                visible_when="error",
                show_border=True,
                label="Error:",
                style_sheet="*{color:red}"
            ),
            label="Output-Port"
        ),
        resizable=True,
        buttons=[ConfirmButton, CancelButton],
        title="Add Output Port",
        width=300,
        height=100,
    )
