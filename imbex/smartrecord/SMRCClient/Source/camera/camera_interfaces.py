"""
.. module: camera_interfaces
.. moduleauthor: Marcel Kennert
"""
from traits.api import HasTraits, Str, List

#=========================================================================
# Interface to define the required properties and methods
# for the camera handler
#=========================================================================


class ICameraProperties(HasTraits):
    """Interface for the camera properties."""

    name = Str()

    image_ext = Str()

    type_extension = Str()

    def save_properties(self):
        """Save the properties of the camera."""
        raise NotImplementedError()

    def load(self, name):
        """Loads the properties of the selected camera.

        :param name: Name of the camera
        :type name: string
        """
        raise NotImplementedError()

    def generate_next_file(self, f):
        """
        With the knowledge of the last file-name can the 
        next file generated.

        :param f: Name of the file
        :type f: string
        :returns: The generated file-name
        :rtype: string
        """
        raise NotImplementedError()

#=========================================================================
# Interface for the handle and communicate with the camera-models
#=========================================================================


class ICameraHandler(HasTraits):
    """
    The camera-handler communicates with the other components
    and calls the functions of the selected camera-model
    """
    listeners = List(ICameraProperties)

    transfer_type = Str()

    def add_listener(self, listener):
        """
        Add a listener in the internal list to inform about modifications.

        :param listener: Listener
        :type listener: object
        """
        self.listeners.append(listener)

    def download_last_image(self):
        """Downloads the last image in the full-resolution and as a preview"""
        raise NotImplementedError()

    def download_reference_image(self):
        """Downloads the last taken image and save it as the reference image"""
        raise NotImplementedError()

#=========================================================================
# Interface for the components which must be inform about new images
#=========================================================================


class ICameraListener(object):
    """Interface to inform the listeners about new images"""

    def update_downloaded_preview(self, fname):
        """Updates the preview

        :param fname: Name of the file
        :type fname: string
        """
        raise NotImplementedError()

    def update_downloaded_image(self, fname):
        """Updates the image

        :param fname: Name of the file
        :type fname: string
        """
        raise NotImplementedError()
