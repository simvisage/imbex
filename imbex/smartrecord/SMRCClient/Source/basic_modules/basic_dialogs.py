"""
.. module: basic_dialogs
.. moduleauthor: Marcel Kennert
"""
"""
The module contains independently dialogs which can be useful
for other classes
"""
from pyface.image_resource import ImageResource
from logging import getLogger
from os import listdir
from os.path import isfile, join

from cv2 import imread, resize, imwrite
from numpy import array
from pyface.api import ProgressDialog
from traits.api import HasTraits, Str, Directory, List
from traitsui.api import View, VGroup, UItem, Image, HGroup, spring,\
    ListEditor, InstanceEditor
from traitsui.menu import OKButton

from application.configuration import images_dir, resized_images_dir
from basic_modules.basic_classes import ImportItem


class ImportManuallyLoader(HasTraits):
    """Provide the manually import from experiments."""

    images = List()

    def __init__(self, values):
        for val in values:
            image, ctime = val
            self.images.append(
                ImportItem(image, self.time_to_secs(int(ctime))))

    def get_images_values(self):
        """Returns all importet images and the recorded values.

        :returns: Images, Values
        :rtype: list, ndarray
        """
        self.resize_images()
        res_imgs, res_vals = [], []
        for img in self.images:
            cur_img, val = img.save()
            res_imgs.append(cur_img)
            res_vals.append(val)
        return res_imgs, array(res_vals[1:])

    def time_to_secs(self, seconds):
        """Converts the given seconds to a time-format.

        :param seconds: Seconds
        :param seconds: int
        :returns: Time-format
        :rtype: string
        """
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return "%02d:%02d:%02d:%02d" % (d, h, m, s)

    def get_all_files(self, directory):
        """
        Returns all files of the directory.

        :param directory: Path to the directory
        :type directory: string
        :returns: Paths of all files
        :rtype: List
        """
        files = [f for f in listdir(directory) if isfile(join(directory, f))]
        return sorted(files)

    def resize_images(self):
        """Resizes all images in the images_dir."""
        files = self.get_all_files(images_dir)
        progress = ProcessDialog(title="Resize images", max_n=len(files))
        for i in range(len(files)):
            f = files[i]
            progress.update(n=i, msg="Resize image: {0}".format(f))
            src = join(images_dir, f)
            dst = join(resized_images_dir, f)
            img = imread(src)
            img = resize(img, (300, 225))
            imwrite(dst, img)
        progress.close()

    view = View(
        VGroup(
            UItem('images', style='readonly',
                  editor=ListEditor(editor=InstanceEditor(), style='custom')
                  ),
            label="Define values"
        ),
        title="Insert values",
        width=500,
        height=500,
        resizable=True,
        buttons=[OKButton],
        icon=ImageResource("../icons/smrc_icon.png")
    )


class StateDialogs(HasTraits):
    """Dialogs to show the process state."""

    successful = Str('The process was successful')

    cancel = Str('The process has been canceled')

    def open_successful(self):
        "Opens the dialog to show that the process was executed successfully."
        self.configure_traits(view='successful_view', kind='livemodal')

    def open_cancel(self):
        "Opens the dialog to show that the process wasn't executed successfully."
        self.configure_traits(view='cancel_view', kind='livemodal')

    successful_view = View(
        UItem('successful', style='readonly'),
        buttons=['OK'],
        resizable=True,
        width=300,
        height=75,
        title='Process',
        icon=ImageResource("../icons/smrc_icon.png")
    )

    cancel_view = View(
        UItem('cancel', style='readonly'),
        buttons=['OK'],
        resizable=True,
        width=300,
        height=75,
        title='Process',
        icon=ImageResource("../icons/smrc_icon.png")
    )


class WarningSystemDialogs(HasTraits):
    """Dialogs to warn the user that can lost some data by closing the app."""

    warning_icon = Image('../../icons/warning.png')

    exit_warning = Str("Do you want exit_view the program?")

    unsaved_warning = Str("The unsaved files will be permanently deleted")

    restart_warning = Str("Do you really want start a new experiment?")

    def open_restart(self):
        """
        Opens a dialog to inform the user that the process will delete data
        by starting a new experiment

        :returns: Returns True if the user press OK, False otherwise
        :rtype: Bool
        """
        return self.configure_traits(view='restart_view', kind='livemodal')

    def open_exit(self):
        """
        Opens a dialog to inform the user that the process will delete data
        by exit the application

        :returns: Returns True if the user press OK, False otherwise
        :rtype: Bool
        """
        return self.configure_traits(view='exit_view', kind='livemodal')

    exit_view = View(
        VGroup(
            HGroup(
                UItem('warning_icon'),
                spring,
            ),
            UItem('exit_warning', style='readonly'),
            UItem('unsaved_warning', style='readonly')
        ),
        buttons=['OK', 'Cancel'],
        resizable=True,
        width=250,
        title='Warning',
        icon=ImageResource("../icons/smrc_icon.png")
    )

    restart_view = View(
        VGroup(
            HGroup(
                UItem('warning_icon'),
                spring,
            ),
            UItem('restart_warning', style='readonly'),
            UItem('unsaved_warning', style='readonly'),
        ),
        buttons=['OK', 'Cancel'],
        resizable=True,
        width=300,
        height=100,
        title='Warning',
        icon=ImageResource("../icons/smrc_icon.png")
    )


class ErrorDialogs(HasTraits):
    """Dialog to show errors"""

    error = Str()

    def open_error(self, msg):
        """Opens the dialog with the given message

        :param msg: Message
        :type msg: string
        """
        self.error = msg
        self.configure_traits(view="error_view", kind="livemodal")

    error_view = View(
        UItem('error', style='readonly'),
        buttons=['OK'],
        resizable=True,
        width=300,
        height=75,
        title='Error',
        icon=ImageResource("../icons/smrc_icon.png")
    )


class WarningDialog(HasTraits):
    """Dialog to show warnings."""
    warning_icon = Image('../../icons/warning.png')

    msg = Str()

    def __init__(self, msg):
        self.msg = msg

    def open(self):
        """
        Opens a dialog to inform the user that the process will delete data
        by exit the application

        :returns: Returns True if the user press OK, False otherwise
        :rtype: Bool
        """
        return self.configure_traits(kind='livemodal')

    view = View(
        VGroup(
            HGroup(
                UItem('warning_icon'),
                spring,
            ),
            UItem('msg', style='readonly'),
        ),
        buttons=['OK', 'Cancel'],
        resizable=True,
        width=300,
        height=75,
        title='Warning',
        icon=ImageResource("../icons/smrc_icon.png")
    )


class SaveDialog(HasTraits):
    """Dialog to save files."""

    dir_name = Directory

    def open(self):
        """
        Opens a dialog to select to select the store-path

        :returns: The selected path
        :rtype: string
        """
        confirm = self.configure_traits(view='show_view', kind='livemodal')
        if confirm:
            return self.dir_name
        else:
            return None

    show_view = View(
        UItem('dir_name'),
        title='Save',
        buttons=['OK', 'Cancel'],
        resizable=True,
        width=300,
        height=100,
        icon=ImageResource("../icons/smrc_icon.png")
    )


class ProcessDialog(object):
    """Open a dialog to show the progress of the process"""

    def __init__(self, title, max_n):
        self.max_n = max_n
        self.progress = ProgressDialog(max=max_n, title=title,
                                       show_time=False, can_cancel=False,
                                       show_percent=True)
        self.progress.open()

    def update(self, n=-1, msg=""):
        """Update the state of the progress.

        :param n: Step
        :type n: int
        :param msg: Description for the step
        :type msg: string
        """
        if n > 0:
            self.progress.update(n)
        if len(msg) > 0:
            self.progress.message = msg

    def close(self):
        """Close the progress-dialog."""
        self.progress.update(self.max_n)


class ApplicationDialogs(HasTraits):
    """Make it possible to use all dialogs with just one instance."""

    error_dialog = ErrorDialogs()

    state_dialogs = StateDialogs()

    warning_dialogs = WarningSystemDialogs()

    save_dialog = SaveDialog()

    logger = getLogger("application")

    def open_restart(self):
        """Opens the restart-dialog."""
        return self.warning_dialogs.open_restart()

    def open_exit(self):
        """Opens the exit-dialog."""
        return self.warning_dialogs.open_exit()

    def open_state(self, state):
        """Opens the state-dialog.

        :param state: True if the process was successful, False otherwise
        :type state: bool
        """
        if state:
            self.state_dialogs.open_successful()
        else:
            self.state_dialogs.open_cancel()

    def open_error(self, msg):
        """Opens the error-dialog

        :param msg: Error-message
        :type msg: string
        """
        self.error_dialog.open_error(msg)

    def open_save(self):
        """Opens the dialog to select the storage path.

        :returns: The selected path
        :rtype: string
        """
        return self.save_dialog.open()

