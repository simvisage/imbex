"""
.. module: measuring_card
.. moduleauthor: Marcel Kennert
"""

from json import dump, load
from logging import getLogger
from os.path import join

from UniversalLibrary import cbAIn, BIPOLAR, BIP10VOLTS
from traits.api import HasTraits, Int, List, Button, Bool
from traitsui.api import View, Item, UItem, ListEditor, HGroup, spring, VGroup

from application.configuration import experiment_dir, measuring_card_file
from measuring_card.ports import InputPort, OutputPort, DialogPortAI,\
    DialogPortDO, PortDO, PortAI


class MeasuringCard(HasTraits):
    """
    MeasuringCard represents the measuring card and the functionality 
    of the card. The class provides the reading of the ports 
    and the digital triggering of the ports.
    """

    id = Int()

    volt_interval = Int(BIP10VOLTS)

    input_ports = List(InputPort)

    output_ports = List(OutputPort)

    logger = getLogger("Application")

    def __init__(self):
        self.dialog_portai = DialogPortAI(self)
        self.dialog_portdo = DialogPortDO(self)
        cbAIn(self.id, 0, BIPOLAR)

    def append_port(self, port):
        """Appends a port to the measuring card.

        :param port: Port which should be add.
        :type port: Port
        :raises: ValueError
        """
        pid = port.id
        if port.is_input_port:
            if self.input_port_exists(pid):
                raise ValueError("Port id is already awarded")
            self.input_ports.append(port)
            self.logger.debug("Append a input-port: {0}".format(port))
        else:
            if self.output_port_exists(pid):
                raise ValueError("Port id is already awarded")
            self.output_ports.append(port)
            self.logger.debug("Append a out-port: {0}".format(port))

    def is_valid(self):
        """
        Checks whether the measuring card have all necessary ports and
        raises a ValueError if something is wrong. 


        :raises: ValueError
        """
        if len(self.input_ports) < 1:
            raise ValueError("Define a input port")
        elif len(self.output_ports) < 1:
            raise ValueError("Define a output port")
    
    @staticmethod
    def generate_input_port():
        port=PortAI.generate_file(0, name="Force [kN]")
        data = {"volt_interval":0, "ports":[port]}
        with open(join(experiment_dir, measuring_card_file), 'w') as f:
            dump(data, f, indent=2)
        
    #=========================================================================
    # Methods for the output ports
    #=========================================================================

    def output_port_exists(self, port_id):
        """Checks whether the given port id already exists.

        :param port_id: Id of the port.
        :type port_id: int
        :returns: True if the id already exists, False otherwise.
        :rtype: bool
        """
        for p in self.output_ports:
            if p.id == port_id:
                return True
        return False

    def trigger_port(self, port_id,  reset=False, reset_time=0):
        """Trigger a digital signal to the given port_id.

        :param port_id: Id of the Port.
        :type port_id: int
        :param reset: True if the value should reset by a given time
        :type reset: bool
        :param reset_time: Time to pass until reset the value
        :type reset_time: float.
        :returns: True if the signal was sent, False otherwise
        :rtype: bool
        :raises: ValueError
        """
        for port in self.output_ports:
            if port.id == port_id:
                if reset:
                    return port.trigger(reset_time)
                else:
                    return port.trigger()
        raise ValueError("The given id not exists")

    def trigger_all_ports(self, reset=True, reset_time=0.1):
        """Trigger a digital signal to all ports.

        :param reset: True if the value should reset by a given time
        :type reset: bool
        :param reset_time: Time to pass until reset the value
        :type reset_time: float
        :returns: True if the signal was sent, False otherwise 
        :rtype: bool
        :raises: ValueError
        """
        self.logger.debug("Trigger_all_ports [MeasuringCard]")
        for port in self.output_ports:
            if reset:
                return port.trigger(reset_time)
            else:
                return port.trigger()
        return True

    #=========================================================================
    # Methods for the input ports
    #=========================================================================

    def input_port_exists(self, port_id):
        """Checks whether the given port id already exists.

        :param port_id: Id of the port.
        :type port_id: int
        :returns: True if the id already exists, False otherwise.
        :rtype: bool
        """
        for p in self.input_ports:
            if p.id == port_id:
                return True
        return False

    def record_port(self, port_id):
        """Records the value of the port by the given port-id.

        :param port_id: Id of the port.
        :type port_id: int
        :returns: (port_id,  value)
        :rtype: List
        :raises: ValueError
        """
        for port in self.input_ports:
            pid = port.id
            if port.id == port_id:
                value = port.record_port(self.volt_interval)
                return (pid, value)
        raise ValueError("The given id not exists.")

    def record_all_ports(self):
        """Records the value of all ports.

        :returns: List that contains  tuples like (port_id, value)
        :rtype: List
        """
        res = []
        for port in self.input_ports:
            value = port.record_port(self.volt_interval)
            res.append((port.id, value))
        return res

    #=========================================================================
    # Methods to save and load the measuring card
    #=========================================================================

    def save(self):
        """Saves the properties of the measuring card in a json-file."""
        self.logger.debug("Save measuring card [MeasuringCard]")
        data = {}
        data["volt_interval"] = self.volt_interval
        data["ports"] = []
        for port in self.input_ports + self.output_ports:
            data["ports"].append(port.save())
        with open(join(experiment_dir, measuring_card_file), 'w') as f:
            dump(data, f, indent=2)
    
    
    def load(self):
        """Loads the properties of the measuring card from a json-file."""
        self.logger.debug("Load measuring card [MeasuringCard]")
        del self.input_ports[:]
        del self.output_ports[:]
        with open(join(experiment_dir, measuring_card_file), 'r') as f:
            data = load(f)
        self.volt_interval = data["volt_interval"]
        ports = data["ports"]
        for port in ports:
            class_name = port['class_name']
            if class_name == "PortDO":
                port = PortDO.load(port, self)
            elif class_name == "PortAI":
                port = PortAI.load(port, self)
            self.append_port(port)

    @staticmethod
    def load_input_ports():
        """Loads the input ports from a json-file."""
        with open(join(experiment_dir, measuring_card_file), 'r') as f:
            data = load(f)
        result = []
        ports = data["ports"]
        for port in ports:
            if port["input"]:
                result.append(PortAI.load(port, None))
        return result

    @staticmethod
    def load_input_ports_as_dict():
        """Loads the input ports as a dictionary."""
        with open(join(experiment_dir, measuring_card_file), 'r') as f:
            data = load(f)
        result = {}
        ports = data["ports"]
        for port in ports:
            if port["input"]:
                result[port["name"]] = port["id"]
        return result

    #=========================================================================
    # Getter functions for other components
    #=========================================================================

    def get_port_name(self, port_id):
        """Returns the name by the given port-id

        :param port_id: Id of the port.
        :type port_id: int
        :returns: Name of the port
        :rtype: str
        :raises: ValueError 
        """
        for p in self.input_ports + self.output_ports:
            if p.id == port_id:
                return p.name
        raise ValueError("The given id not exists.")

    def get_all_ports(self):
        """Returns all ports

        :returns: All configured ports
        :rtype: List(Port)
        """
        return self.input_ports + self.output_ports

    def get_values_as_string(self):
        """"Returns the current values of the ports as a string

        :returns: Recorded values as a string
        :rtype: string
        """
        res = ""
        for p in self.input_ports:
            pid, pname = p.id, p.name
            value = self.record_port(pid)[1]
            res += "{0}: {1:.3f}; ".format(pname, value)
        return res

    #=========================================================================
    # Traitsview + Traitsevents
    #=========================================================================

    started = Bool(False)

    add_portai = Button("Add Analog Input Port")

    add_portdo = Button("Add Digital Output Port")

    def _add_portdo_fired(self):
        # Open a dialog to add a new digital output port
        self.dialog_portdo.parent = self
        confirm = self.dialog_portdo.open_dialog()
        if confirm:
            self.append_port(self.dialog_portdo.load())

    def _add_portai_fired(self):
        # Open a dialog to add a new analog input port
        self.dialog_portai.parent = self
        confirm = self.dialog_portai.open_dialog()
        if confirm:
            self.append_port(self.dialog_portai.load())

    view = View(
        VGroup(
            VGroup(
                UItem("input_ports", label="Input-Ports", style="custom",
                      editor=ListEditor(use_notebook=True, deletable=True,
                                        page_name=".name")),
                HGroup(spring,
                       Item("add_portai", show_label=False)),
                label="Input-Ports",
            ),
            VGroup(
                UItem("output_ports", label="Output-Ports", style="custom",
                      editor=ListEditor(use_notebook=True, deletable=True,
                                        page_name=".name")),
                HGroup(spring,
                       Item("add_portdo", show_label=False)),
                label="Output-Ports"
            ),
            layout="normal",
            enabled_when="not started"
        ),
        resizable=True,
    )
