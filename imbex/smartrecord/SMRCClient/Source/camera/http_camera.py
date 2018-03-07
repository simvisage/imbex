"""
.. module: http_camera
.. moduleauthor: Marcel Kennert
"""
from json import dump, load
from logging import getLogger
from os.path import join, basename
from re import split
from threading import Lock
from time import sleep
from urllib import urlretrieve

from requests import get, ConnectionError
from traits.api import Button, Bool, Str, Instance, List
from traitsui.api import View, UItem, Group, VGroup, HGroup, Item

from application.configuration import cameras_dir
from application.configuration import images_dir, image_file, resized_images_dir
from basic_modules.basic_classes import RunThread, Combobox
from basic_modules.basic_methods import \
    convert_number, resize_image, get_all_files
from camera.camera_interfaces import ICameraProperties, ICameraHandler

#=========================================================================
# Properties to transfer the images via WLAN
#=========================================================================


class HTTPCameraProperties(ICameraProperties):
    """
    Sets the camera properties with a HTTP-interface. 
    By defaults will set the camera properties of the model Pentax K-70.
    """

    camera_models = Instance(Combobox, ())

    ip_address = Str("192.168.0.1")

    url = "http://{0}/v1/photos"

    url_photo = "{0}/{1}/{2}"

    logger = getLogger("Application")

    def __init__(self, create_default=True):
        self.type_extension = "_http"
        if create_default:
            self.name = "Pentax-K70"
            self.image_ext = ".JPG"
            self.save_properties()
        self.update_camera_models()
        self.camera_models.add_listener(self)

    def update_camera_models(self):
        """Updates the camera models in the Combobox."""
        self.camera_models.reset()
        files = get_all_files(cameras_dir)
        for f in files:
            if self.type_extension in f:
                fpath = join(cameras_dir, f)
                data = self.load(fpath)
                self.camera_models.add_item(data["name"], fpath)

    def save_properties(self):
        """Save the properties of the camera."""
        try:
            fname = self.name + self.type_extension + ".json"
            with open(join(cameras_dir, fname), 'w') as f:
                dump({'name': self.name,
                      'image_ext': self.image_ext,
                      'url': self.url}, f)
        except Exception, e:
            self.logger.error(str(e))

    def update_properties(self, data):
        """Update the properties of the camera.

        :param data: Properties of the camera.
        :type data: Dictionary
        """
        if data != None:
            self.name = data['name']
            self.url = data['url']
            self.image_ext = data['image_ext']

    def load(self, f):
        """Loads the properties by the given file.

        :param file: File of the camera.
        :type file: string
        """
        try:
            with open(f) as data_file:
                data = load(data_file)
        except Exception, e:
            self.logger.error(str(e))
            return None
        return data

    def generate_next_file(self, f):
        "With the knowledge of the last file-name can the next file generated."
        args = filter(None, split(r'(\d+)', f))
        fn = int(args[1]) + 1
        return "{0}{1}{2}".format(args[0], fn, args[2])

    def selected_changed(self, selected_key):
        """Update the properties when the user select a new camera."""
        data = self.load(self.camera_models.get_selected_value())
        self.update_properties(data)

    view = View(
        VGroup(
            Item('camera_models', label="Camera:", style="custom"),
            Item('name', style='readonly'),
            Item('ip_address', label='IP:'),
            Item('image_ext', label='Ext:', style='readonly'),
            label='Properties',
            show_border=True
        )
    )

#=========================================================================
# Handler to transfer the images via HTTP-request
#=========================================================================


class HTTPCameraHandler(ICameraHandler):
    """
    Handles the communication with the components and the camera.
    The HTTPCameraHandler transfer the images via HTTP-request
    """

    camera_model = Instance(HTTPCameraProperties, ())

    lock = Lock()

    listeners = List()
    
    logger = getLogger("Application")
    
    def __init__(self):
        self.img_num = 0
        self.download_image = Bool(False)
        self.queue = []
        self.queue_preview = []
        self.transfer_type = "HTTP"

    def download_last_image(self):
        """Downloads the last image in the full-resolution and as a preview"""
        # wait 2 seconds before transfer the image to make sure that
        # that the camera safes the last image
        sleep(2)
        folder, f = self.get_last_folder_file()
        url_photo = self.camera_model.url_photo.format(self.url, folder, f)
        self.img_num = self.img_num + 1
        fname = image_file.format(convert_number(self.img_num),
                                  self.camera_model.image_ext)
        self.append_preview_to_queue(url_photo, fname)
        self.append_image_to_queue(join(images_dir, fname), fname, url_photo)

    def download_reference_image(self):
        """Downloads the last taken image and save it as the reference image"""
        f = image_file.format(convert_number(0), self.camera_model.image_ext)
        fpath = join(images_dir, f)
        folder, f = self.get_last_folder_file()
        url_photo = self.camera_model.url_photo.format(self.url, folder, f)
        self.append_image_to_queue(fpath, f, url_photo, threading=False)
        resize_image(fpath)

    def append_image_to_queue(self, fpath, fname, url_photo, threading=True):
        # Appends a image to the event queue
        try:
            with self.lock:
                self.queue.append((url_photo, fpath))
            if threading and not self.download_image:
                # Do not start a new thread if one is already running
                RunThread(target=self._download_images_in_background)
            elif not threading:
                # Do not download the images in the background
                self._download_images_in_background()
        except Exception, e:
            msg = "Image: {0} Exception: {1}".format(self.img_num, str(e))
            self.logger.error(msg)

    def _download_images_in_background(self):
        # download the images
        self.state = "Download image"
        self.download_image = True
        while len(self.queue) > 0:
            try:
                with self.lock:
                    url_photo, fpath = self.queue.pop(0)
                urlretrieve(url_photo, fpath)
                if self.img_num > 0:
                    for listener in self.listeners:
                        listener.update_downloaded_image(basename(fpath))
                self.logger.debug("Downloaded image: {0}".format(fpath))
            except Exception, e:
                self.logger.error(str(e))
        self.state = "Download finished"
        self.download_image = False

    def append_preview_to_queue(self, url, fname):
        # Appends a preview to the event queue
        try:
            with self.lock:
                self.queue_preview.append((url, fname))
            RunThread(target=self._download_previews_in_background)
        except Exception, e:
            msg = "Image: {0} Exception: {1}".format(self.img_num, str(e))
            self.logger.error(msg)

    def _download_previews_in_background(self):
        # download previews
        while len(self.queue_preview) > 0:
            try:
                with self.lock:
                    url, fname = self.queue_preview.pop(0)
                fpath = join(resized_images_dir, fname)
                urlretrieve(url + "?size=view", fpath)
                resize_image(fpath, self.img_num > 0)
                if self.img_num > 0:
                    for listener in self.listeners:
                        listener.update_downloaded_preview(fname)
            except Exception, e:
                self.logger.error(str(e))

    def get_last_folder_file(self):
        try:
            self.url = self.camera_model.url.format(
                self.camera_model.ip_address)
            r = get(self.url).json()
            self.folder = r['dirs'][-1]
            self.f = self.folder['files'][-1]
            res = [self.folder['name'], self.f]
        except Exception:
            self.f = self.camera_model.generate_next_file(self.f)
            res = [self.folder['name'], self.f]
            sleep(5)
        return res

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    connect_btn = Button('Connect')

    connected = Bool(False)

    try_to_connect = Bool(False)

    state = Str('Not connected')

    error = Bool(False)

    error_msg = Str('Make sure that the ip-address is correct')

    def _connect_btn_fired(self):
        RunThread(target=self._connect)

    def _connect(self):
        self.state = "Try to connect with the camera"
        self.try_to_connect = True
        try:
            self.url = self.camera_model.url.format(
                self.camera_model.ip_address)
            get(self.url).json()
            self.state = 'Connected'
            self.connected = True
            self.error = False
        except ConnectionError:
            self.state = 'Not connected'
            self.error = True
            self.connected = False
        self.try_to_connect = False

    view = View(
        VGroup(
            HGroup(
                UItem('state', style='readonly'),
            ),
            UItem(
                'camera_model', enabled_when='not connected', style='custom'),
            UItem('connect_btn', enabled_when='not connected'),
            Group(
                UItem("error_msg", style="readonly"),
                visible_when="error",
                style_sheet="*{color:red}"
            ),
            layout='normal',
            label='Camera',
            enabled_when='not try_to_connect'
        ),
        height=220,
        width=250,
    )
