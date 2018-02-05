"""
.. module: camera_selector
.. moduleauthor: Marcel Kennert
"""
from traits.api import HasTraits, Instance, List
from traitsui.api import View, Item, UItem, ListEditor, VGroup
from basic_modules.basic_classes import Combobox
from camera.http_camera import HTTPCameraHandler
from camera.camera_interfaces import ICameraHandler


# Here you can add more transfer types
all_transfer_types = {"HTTP": HTTPCameraHandler()}


class CameraSelector(HasTraits):
    """
    CameraSelector was developed to make it possible to 
    add new transfer type. 
    """
    type = Instance(Combobox, ())

    type_views = List(ICameraHandler)

    def __init__(self):
        for t in all_transfer_types:
            self.type.add_item(t, all_transfer_types[t])
            self.type_views.append(all_transfer_types[t])

    def selected_changed(self, selected_key):
        """Updates the view when the selected_key has changed.
        
        :param selected_key: Selected transfer-type
        :type selected_key: string
        """
        if selected_key in all_transfer_types:
            del self.type_views[:]
            self.type_views.append(all_transfer_types[selected_key])

    def add_listener(self, listener):
        """Add a listener in the internal of all types.

        :param listener: Listener
        :type listener: object
        """
        for t in all_transfer_types:
            all_transfer_types[t].add_listener(listener)

    def download_last_image(self):
        """Downloads the last image in the full-resolution and as a preview"""
        t = self.type.get_selected_value()
        t.download_last_image()

    def download_reference_image(self):
        """Downloads the last taken image and save it as the reference image"""
        t = self.type.get_selected_value()
        t.download_reference_image()

    view = View(
        Item('type', style='custom', label="Transfer type"),
        VGroup(
            UItem('type_views', style='custom',
                  editor=ListEditor(use_notebook=True, deletable=False,
                                    page_name='.transfer_type')
                  )
        )
    )
