"""
.. module: experiment_type
.. moduleauthor: Marcel Kennert
"""
from datetime import datetime
from json import load
from os.path import join

from enclosure.base.server_license_data import json
from traits.api import HasTraits, Str, Instance, Date, Bool
from traitsui.api import View, Item, UItem, VGroup
from traitsui.menu import Action

from application.configuration import experiment_dir, experiment_type_file
from basic_modules.basic_methods import \
    convert_date_to_string, convert_string_to_date
from experiment.type.reinforcement.reinforcements import ReinforcementSelector
from experiment.type.shape.shape_selector import ShapeSelector
from experiment.type.types.type_selector import TypeSelector, TypeSerieDialog
from server.ldap_server import LDAPUsers


class ExperimentType(HasTraits):
    """Defines the properties of the experiment."""
    #=========================================================================
    # Important components
    #=========================================================================
    
    type = Instance(TypeSelector)

    shape = Instance(ShapeSelector, ())

    reinforcement = Instance(ReinforcementSelector, ())

    server_attributes = TypeSerieDialog()

    #=========================================================================
    # Attributes of the experiment
    #=========================================================================

    name = Str()

    start_date = Date()

    ldap_users = Instance(LDAPUsers, ())

    record_mode = Bool(False)

    def __init__(self):
        self.start_date = datetime.today()
        self.fpath = join(experiment_dir, experiment_type_file)
        self.type = TypeSelector(parent=self)

    def update_series(self, experiment=None):
        if experiment == None:
            experiment = self.type.get_type()
        try:
            series = self.exp_model.update_series(experiment)
        except Exception:
            return []
        self.type.update_series(series)
        return series

    def get_type_serie(self):
        return (self.type.get_type(), self.type.get_serie())
   
    def get_user_serie_type(self):
        t = self.type.get_type()
        s = self.type.get_serie()
        if s == 'None':
            try:
                user, serie = self.server_attributes.open(
                    self.ldap_users.users._get_options(), self.update_series(t))
            except Exception:
                return None
        return (user, serie, t)

    def is_valid(self):
        if len(self.name) < 1:
            raise ValueError("Define a name for the experiment")

    def save(self):
        t = self.type.get_selected_value()
        s = self.type.get_serie()
        data = {'name': self.name,
                'ldap_users': self.ldap_users.get_user(),
                'start_date': convert_date_to_string(self.start_date),
                'type': t.type_name.lower(),
                'type_data': t.save(),
                'shape': self.shape.get_selected_key(),
                'shape_data': self.shape.save(),
                'reinforcement': self.reinforcement.save(),
                'serie': s
                }
        with open(self.fpath, 'wb') as f:
            json.dump(data, f)
        return self.generate_file_name()

    def load(self):
        with open(self.fpath, 'r') as f:
            data = load(f)
        self.name = data['name']
        self.start_date = convert_string_to_date(data['start_date'])
        user = data['ldap_users']
        serie = data['serie']
        t = data['type']
        if serie == 'None':
            user, serie = self.server_attributes.open(
                self.ldap_users.users._get_options(), self.update_series(t))
        self.reinforcement.load(data['reinforcement'])
        self.shape.load(data['shape_data']['shape'])
        self.ldap_users.show_user(user)
        self.type.set_serie(serie)
        self.type.load_type(data)

    @staticmethod
    def open(exp_model):
        experiment_type = ExperimentType()
        experiment_type.record_mode = True
        experiment_type.show_dialog = True
        experiment_type.exp_model = exp_model
        experiment_type.update_series()
        if experiment_type.configure_traits(kind='livemodal'):
            experiment_type.save()
            experiment_type.load()
            return True
        return False

    def generate_file_name(self):
        args = [convert_date_to_string(self.start_date), self.name,
                self.ldap_users.get_user()]
        return "{0}_{1}_{2}".format(*args)
    
    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    show_dialog = Bool(False)

    ConfirmButton = Action(name="OK", enabled_when="not error",
                           visible_when="show_dialog")

    view = View(
        VGroup(
            VGroup(
                Item('name'),
                Item('ldap_users', style='custom'),
                Item('start_date'),
            ),
            UItem('type', style='custom'),
            UItem('shape', style='custom'),
            UItem('reinforcement', style='custom'),
            enabled_when='record_mode'
        ),
        buttons=[ConfirmButton]
    )
