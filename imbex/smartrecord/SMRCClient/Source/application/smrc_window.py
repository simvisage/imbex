"""
.. module: smrc_window
.. moduleauthor: Marcel Kennert
"""
from logging import getLogger
from time import time, sleep

from pyface.image_resource import ImageResource
from traits.api import HasTraits, Instance, Str, Bool
from traitsui.api import View, UItem, MenuBar, Menu, StatusItem, ToolBar

from basic_modules.basic_classes import RunThread
from basic_modules.basic_methods import secs_to_time
from application.smrc_handler import \
    toolbar_actions, SMRCHandler, help_docs, file_actions, configure_actions,\
    import_action
from application.smrc_model import SMRCModel


class SMRCWindow(HasTraits):
    """
    SMRCWindow is the Mainwindow of the application SmartRecord. The window 
    shows the time and the current phase of the experiment when it's running. 
    Furthermore the window interacts with the SMRCModel and 
    make it possible that the user can start and 
    cancel the experiment by clicking a icon.
    """

    model = Instance(SMRCModel)

    smrc_handler = SMRCHandler()

    current_phase = Str("Current Phase - Not Started")

    clock = Str(secs_to_time(0))

    record_mode = Bool(True)

    def __init__(self, model):
        self.logger = getLogger("application")
        self.logger.debug("Initializes SMRCWindow")
        self.record_mode = model.record_mode
        self.model = model
        self.model.experiment.window = self

    def start_clock(self):
        """Run the clock in the status bar."""
        self.logger.info("Start the time-thread [SMRCWindow]")
        self.clock = secs_to_time(0)
        RunThread(target=self._run_clock)

    def _run_clock(self):
        # Updates the status bar time once every second.
        self.clock_running = True
        self.start_time = time()
        while self.clock_running:
            self.td = time() - self.start_time
            self.clock = secs_to_time(self.td)
            sleep(1.0)

    #=========================================================================
    # Traitsview
    #=========================================================================

    # Switch to stop the running thread
    clock_running = Bool(False)

    view = View(
        UItem("model", style="custom"),
        menubar=MenuBar(Menu(*file_actions, name="File"),
                        Menu(*configure_actions, name="Configuration"),
                        Menu(*import_action, name="Import"),
                        Menu(help_docs, name="Help")),
        toolbar=ToolBar(*toolbar_actions, show_tool_names=False,
                        image_size=(30, 30)),
        statusbar=[StatusItem(name="current_phase", width=0.5),
                   StatusItem(name="clock", width=85)],
        handler=smrc_handler,
        resizable=True,
        height=680,
        width=1300,
        title="SmartRecord",
        icon=ImageResource("../../icons/smrc_icon.png")
    )
