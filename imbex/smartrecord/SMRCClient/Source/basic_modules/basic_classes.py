"""
.. module: basic_classes
.. moduleauthor: Marcel Kennert
"""
import warnings
warnings.filterwarnings("ignore")
from copy import deepcopy
from threading import Thread
from numpy import array
from traits.api import Str, Instance, HasTraits, Dict, Property
from traitsui.api import \
    Item, UItem, InstanceEditor, View, CheckListEditor, HGroup


class RunThread(Thread):
    """Thread which start automatically with the daemon-flag."""

    def __init__(self, *args, **kw):
        super(RunThread, self).__init__(*args, **kw)
        self.daemon = True
        self.start()


class InstanceUItem(UItem):
    """Convenience class for including an Instance in a View."""

    style = Str("custom")

    editor = Instance(InstanceEditor, ())


class ImportItem(HasTraits):
    """Item which will used by the import of old projects."""
    image = Str()

    time = Str()

    value = Str(0)

    def __init__(self, image, time):
        self.image = image
        self.time = time

    def time_to_secs(self, tfmt):
        """Converts the given time-format to seconds.

        :param tfmt: Time-format
        :type tfmt: string
        :returns: seconds
        :rtype: int
        """
        splt = array(tfmt.split(":"), int)
        t = splt[0] * 24 * 60 * 60 + splt[1] * \
            60 * 60 + splt[2] * 60 + splt[3]
        return t

    def save(self):
        """Returns the properties of the item. 

        :returns: Name of the image, (past time, recorded value)
        :rtype: (string, list)
        """
        return self.image, [self.time_to_secs(self.time), float(self.value)]

    view = View(
        HGroup(
            Item("image", style='readonly'),
            Item("time", style='readonly'),
            Item("value")
        )
    )


class Combobox(HasTraits):
    """Combobox in traits."""

    listeners = []

    values = Dict()

    selected_key = Str

    options = Property(Str, depends_on="values")

    def add_item(self, key, value):
        """Add a item in the dictionary and show it in the combobox

        :param key: Key which should show in the combobox
        :type key: string
        :param value: Belonging value
        :type value: object
        """
        self.values[key] = value
        if len(self.selected_key) < 1:
            self.selected_key = key

    def reset(self):
        """Resets all entries of the dictionary"""
        vals = deepcopy(self.values)
        for key in vals:
            if self.values.has_key(key):
                del self.values[key]
        self.selected_key = ""

    def show_value(self, value):
        """Shows the key of the given value

        :param value: Belonging value
        :type value: object
        """
        for key in self.values:
            if self.values[key] == value:
                self.selected_key = key

    def add_listener(self, listener):
        """
        Makes it possible that the parents can be notify 
        when the selected_key has changed.

        :param listener: Parent object
        :type listener: object
        """
        self.listeners.append(listener)

    def _selected_key_changed(self):
        # Notifies the listeners that the selected_key has changed.
        for listener in self.listeners:
            listener.selected_changed(self.selected_key)

    def _get_options(self):
        # Returns all keys
        return sorted(self.values.keys())

    def get_selected_value(self):
        # Returns the value of the selected key
        try:
            res = self.values[self.selected_key]
        except Exception:
            res = 'None'
        return res

    traits_view = View(
        UItem(name="selected_key", editor=CheckListEditor(name="options"),
              style_sheet='*{background-color:None}'),
    )
