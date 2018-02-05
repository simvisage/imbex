'''
Created on 17.11.2017

@author: mkennert
'''
from logging import getLogger
from os.path import basename

from traits.api import HasTraits, Str, List, Instance, Any, Button, Bool
from traitsui.api import TreeEditor, TreeNode, View, UItem, VGroup, HGroup, Group

from basic_modules.basic_classes import Combobox


class CreateSerie(HasTraits):

    name = Str()

    def open(self):
        confirm = self.configure_traits(kind='livemodal')
        if confirm and len(self.name) > 0:
            return True
        else:
            return False

    view = View(
        UItem('name'),
        title='Create Serie',
        buttons=['OK', 'Cancel']
    )


class Experiment(HasTraits):
    name = Str()
    path = Str()


class Serie(HasTraits):
    name = Str()
    path = Str()
    experiments = List(Experiment)


class ExperimentType(HasTraits):
    name = Str()
    series = List(Serie)
    path = Str()


class RootNode(HasTraits):
    name = Str()
    path = Str()
    experiments = List(ExperimentType)


def _tree_editor(selected=''):
    return TreeEditor(
        nodes=[
            TreeNode(node_for=[RootNode],
                     auto_open=True,
                     children='',
                     label='name',
                     view=View(Group('name',
                                     orientation='vertical',
                                     show_left=True))),
            TreeNode(node_for=[RootNode],
                     auto_open=True,
                     children='experiments',
                     label='=experiments',
                     delete_me=False,
                     add=[ExperimentType]),
            TreeNode(node_for=[ExperimentType],
                     auto_open=True,
                     children='series',
                     label='name',
                     delete_me=False,
                     insert=False,
                     add=[Serie]),
            TreeNode(node_for=[Serie],
                     auto_open=True,
                     children='experiments',
                     label='name',
                     insert=False,
                     delete_me=False,
                     add=[Experiment]),
            TreeNode(node_for=[Experiment],
                     auto_open=True,
                     label='name',
                     delete_me=False,
                     rename=False,
                     insert=False)
        ],
        editable=False,
        selected=selected,
        hide_root=True,
        auto_open=0,
    )


class TreeView(HasTraits):
    name = Str('<unknown>')

    root = Instance(RootNode)

    node = Any

    view = View(
        Group(
            UItem(name='root', editor=_tree_editor(selected='node'),
                  resizable=True),
            scrollable=True,
        ),
    )


class ProjectHandler(HasTraits):

    seriedialog = CreateSerie()

    name = Str('<unknown>')

    root = Instance(RootNode)

    node = Any

    combobox = Instance(Combobox, ())

    logger = getLogger("Application")

    def __init__(self, parent):
        self.logger.debug("Initialize ProjectHandler")
        self.parent = parent
        self.root = RootNode(name="smartrecord")
        self.combobox.add_item("Create serie", self._create_serie)
        self.combobox.add_item("Send project", self._send_project)
        self.combobox.add_item("Load project", self._load_project)

    def update_structure(self, experiment_types):
        for exp_type in experiment_types:
            self.root.experiments.append(exp_type)

    def _send_project(self):
        self.parent.send_project()

    def _load_project(self):
        self.parent.load_project(self.node.path)

    def _create_serie(self):
        if self.seriedialog.open():
            n = self.seriedialog.name
            if self.node == None:
                return
            if self.parent.create_serie(self.node.path, n):
                serie = Serie(name=n, path=self.node.path + '/' + n)
                exp_type = basename(self.node.path)
                for exp in self.root.experiments:
                    if exp_type == exp.name:
                        exp.series.append(serie)

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    exe_btn = Button("execute")

    error_msg = Str("The project does already exist")

    error = Bool(False)

    def _exe_btn_fired(self):
        self.combobox.get_selected_value()()

    view = View(
        VGroup(
            UItem(name='root', editor=_tree_editor(selected='node'),
                  resizable=True),
            HGroup(
                UItem("combobox", style="custom"),
                UItem("exe_btn")
            ),
            label="Projects"
        ),
        resizable=True,
    )
