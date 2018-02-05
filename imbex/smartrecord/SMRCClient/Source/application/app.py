"""
.. module: app
.. moduleauthor: Marcel Kennert
"""
from os.path import abspath, dirname
import sys
import warnings
warnings.filterwarnings("ignore")

from pyface.image_resource import ImageResource
from traits.api import HasTraits, Bool
from traitsui.api import Handler, View, UItem, Image

sys.path.append(dirname(dirname(abspath('app.py'))))

from basic_modules.basic_classes import RunThread
from basic_modules.basic_methods import \
    create_dir, clear_temp_folder, create_logger


class Application(object):
    """
    SMRC is a application to record experiment with digital camera 
    automatically and evaluate the experiment with ncorr.  
    """

    # Creates the directories to save the configuration
    # of the application.
    create_dir()

    # Clear the whole temp-folder
    clear_temp_folder()

    # Creates the logger 'application' to save all actions of
    # the application.
    logger = create_logger("Application")

    def __init__(self):
        start_dialog = StartDialog(self)
        start_dialog.show(self.initialize)

    def initialize(self):
        "Initialize the application."
        from application.smrc_model import SMRCModel
        from application.smrc_window import SMRCWindow
        try:
            self.model = SMRCModel(record_mode=True)
            self.logger.info("Application starts in record-mode")
        except Exception, e:
            self.logger.debug(str(e))
            self.logger.info("Application starts in evaluate-mode")
            self.model = SMRCModel(record_mode=False)
        self.window = SMRCWindow(model=self.model)
        self.model.smrc_window = self.window


class StartDialogHandler(Handler):
    """
    Handles the StartDialog. The handler makes sure that the 
    StartDialog will close when the initialization is done.
    """

    def object__close_changed(self, info):
        if info.initialized:
            info.ui.dispose()
            self.close(info, is_ok=True)
            info.object.application_window.configure_traits()


class StartDialog(HasTraits):
    """The StartDialog will show when initializing the application."""

    _close = Bool(False)

    startview = Image("../icons/startview.jpg")

    def __init__(self, parent):
        self.parent = parent
        self.application_window = None

    def initialize(self):
        """Performs the initializing of the application."""
        self.task()
        self.application_window = self.parent.window
        self._close = True

    def show(self, task):
        """
        Show the StartDialog and initialize the application in the background.

        :param task: Task 
        :type task: Built-in function
        """
        self.task = task
        RunThread(target=self.initialize)
        self.configure_traits()

    startdialog = View(
        UItem('startview'),
        handler=StartDialogHandler(),
        width=600,
        height=300,
        title="SmartRecord",
        icon=ImageResource("../icons/smrc_icon.png")
    )

if __name__ == '__main__':
    Application()