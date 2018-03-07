"""
.. module: type_selector
.. moduleauthor: Marcel Kennert
"""
from traits.api import HasTraits, Instance, List, Bool
from traitsui.api import View, Item, VGroup

from basic_modules.basic_classes import Combobox
from experiment.type.types.all_types import IExperimentType, all_types


class TypeSerieDialog(HasTraits):

    ldap_users = Instance(Combobox, ())

    series = Instance(Combobox, ())

    def update_series(self, series):
        """Updates the series in the combobox.

        :param series: Series
        :type series: List(string)
        """
        self.series.reset()
        for s in series:
            self.series.add_item(s, s)

    def update_users(self, users):
        """Updates the LDAP-users in the combobox.

        :param users: LDAP-Users
        :type users: List(string)
        """
        self.ldap_users.reset()
        for u in users:
            self.ldap_users.add_item(u, u)

    def save(self):
        """Returns the selected user and the selected serie.

        :returns: (selected user, selected serie)
        :rtype: Tuple
        """
        return (self.ldap_users.selected_key, self.series.selected_key)

    def open(self, users, series):
        """
        Updates the properties and open a dialog to select the serie and user.

        :param users: LDAP-Users
        :type users: List(Tuple)
        :param series: Series of the selected experiment.
        :type series: List(Tuple)
        :returns: (selected user, selected serie)
        :rtype: Tuple
        """
        self.update_series(series)
        self.update_users(users)
        self.configure_traits(kind='livemodal')
        return self.save()

    view = View(
        Item('ldap_users', style='custom'),
        Item('series', style='custom'),
        title='Create Serie',
        buttons=['OK']
    )


class TypeSelector(HasTraits):

    type = Instance(Combobox, ())

    type_views = List(IExperimentType)

    series = Instance(Combobox, ())

    no_series = Bool(True)

    def __init__(self, parent):
        self.parent = parent
        for t in all_types:
            self.type.add_item(t, all_types[t])
            self.type_views.append(all_types[t])
        self.type.add_listener(self)
        
    def update_series(self, series):
        """Update all series.

        :param series: Series from the server
        :type series: List(string)
        """
        self.series.reset()
        if len(series) > 0:
            self.no_series = False
        for exp in series:
            self.series.add_item(exp, exp)

    def load_type(self, data):
        """Loads the type of the dictionary.

        :param data: Type information
        :type data: Dictionary
        """
        t = data['type']
        for key in all_types:
            if t == key:
                all_types[t].load(data['type_data'])
                all_types[t].show = True
                self.type.show_value(all_types[t])
            else:
                all_types[t].show = False

    def get_selected_value(self):
        """Returns the selected value-type.

        :returns: Selected type
        :rtype: IExperimentType
        """
        return self.type.get_selected_value()

    def get_type(self):
        """Returns the selected name of the selected type.

        :returns: Selected type-name
        :rtype: string.
        """
        return self.type.selected_key

    def get_serie(self):
        """
        Returns the selected serie. If the series can not be loaded from
        the server, return None.

        :returns: The selected serie.
        :rtype: string
        """
        if self.no_series:
            return 'None'
        else:
            return self.series.selected_key
        
    def set_serie(self, serie):
        """Set the selected serie by the given serie.

        :param serie: Serie which should selected
        :type serie: string.
        """
        self.series.selected_key = serie
    
    def selected_changed(self, selected_key):
        for key in all_types:
            if selected_key==key:
                self.parent.update_series(selected_key)
                return
    
    view = View(
        VGroup(
            Item('type', style='custom'),
            Item('series', style='custom', enabled_when="not no_series")
        )
    )
