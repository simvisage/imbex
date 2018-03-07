"""
.. module: travel_sensor
.. moduleauthor: Marcel Kennert
"""
from decimal import Decimal
from json import dump
from json import load as jload
from os.path import join, basename

from PySide.QtCore import Qt
from PySide.QtGui import QMainWindow
from cv2 import imread, resize, imwrite
from numpy import array, save, zeros, ogrid, load, loadtxt
from pyface.image_resource import ImageResource
from traits.api import HasTraits, List, Str, Int, Bool, Instance, Button
from traitsui.api import Handler, UIInfo
from traitsui.api import View, UItem, HGroup, VGroup, Item, Image

from application.configuration import \
    images_dir, travel_sensor_draw_images_dir,\
    displacement_u_dir, travel_sensor_images_dir, sensor_json,\
    displacement_v_dir, stylesheet_smrc, toolbar_background
from application.configuration import travel_sensor_sensors_dir
from basic_modules.basic_dialogs import ProcessDialog, ErrorDialogs
from basic_modules.basic_methods import get_all_files
from experiment.correlation.draw_object.draw_methods import TravelSensorDraw


class Sensor(HasTraits):
    """Represents a virtual travel sensor."""

    points = List()

    name = Str()

    radius = Int()

    def __init__(self, name, points=[]):
        self.name = name
        self.points = points
        self.values = []
        self.parent = None
        self.plot_color = None

    def append_values(self, values):
        """Appends values from a image to the values container.

        :param values: Recorded values of the image.
        :type values: List(float)
        """
        self.values.append(values)

    def save(self):
        """Saves the properties in a npy-file and json-file."""
        save(join(travel_sensor_sensors_dir, '{0}.npy'.format(self.name)),
             array(self.values))
        fpath = join(travel_sensor_sensors_dir, sensor_json.format(self.name))
        data = {'name': self.name, 'points': self.points}
        with open(fpath, 'w') as f:
            dump(data, f)

    @staticmethod
    def load(fpath, values=True):
        """Loads the properties of the travel-sensor.

        :param fpath: Name of the file
        :type fpath: string.
        :returns: The loaded travel-sensor.
        :rtype: Sensor
        """
        name = basename(fpath).split('.')[0]
        with open(join(travel_sensor_sensors_dir, sensor_json.format(name))) as f:
            data = jload(f)
        sensor = Sensor(name, data['points'])
        if values:
            sensor.values = load(fpath)
        return sensor

    def get_values(self, index):
        """Returns the values of the given column-index. 
        [u-displacement, v-displacement, strain_exx,strain_ex,strain_eyy]

        :param index: Index of the column.
        :type index: int.
        :returns: The values of the column.
        :rtype: ndarray
        """
        res = []
        print len(self.values), self.values
        for i in range(len(self.values)):
            res.append(self.values[i][index])
        return array(res)

    def get_average_values(self, arr):
        """Returns the average-value of the circles.

        :param arr: Values
        :type arr: ndarray
        :returns: Average values
        :rtype: float
        """
        self.points = sorted(self.points, key=lambda tup: (tup[0], tup[1]))
        p1, p2 = self.points
        x1, y1 = p1
        x2, y2 = p2
        a1 = self.get_average(arr, y1, x1)
        a2 = self.get_average(arr, y2, x2)
        return float(a2 - a1)

    def get_average(self, arr, y, x):
        """Returns the average-value of the circle by the given positon."""
        m, n = arr.shape[:2]
        y, x = ogrid[-y:m - y, -x:n - x]
        mask = x * x + y * y <= self.radius**2
        array = zeros((m, n), dtype=bool)
        array[mask] = 1
        counter = Decimal(0.0)
        s = Decimal(0.0)
        for i in range(m):
            for j in range(n):
                if array[i, j] > 0:
                    counter += Decimal(1.0)
                    s += Decimal(arr[i, j])
        return s / Decimal(counter)

    def __str__(self, *args, **kwargs):
        return "Name: {0}".format(self.name)

    #=========================================================================
    # Traitsview + Traitsevents
    #=========================================================================

    is_checked = Bool(True)

    def _is_checked_changed(self):
        self.parent.update_plot()

    view = View(
        HGroup(
            UItem('is_checked'),
            UItem('name', style='readonly')
        )
    )


class SensorHandler(Handler):
    """Handles the interaction with the SMRCModel and the SMRCWindow."""

    # The UIInfo object associated with the view
    info = Instance(UIInfo)

    def init(self, info):
        info.ui.control.setContextMenuPolicy(Qt.NoContextMenu)
        for c in info.ui.control.children():
            if isinstance(c, QMainWindow):
                c.setContextMenuPolicy(Qt.NoContextMenu)
        info.ui.control.setStyleSheet(stylesheet_smrc)


class SensorDialog(HasTraits):
    """Dialog to set the sensors manually."""
    fname = Str()

    sensors = List(Sensor)

    sensor_draw = Instance(TravelSensorDraw, ())

    max_image_number = Int(0)

    cur_image_number = Int(0)

    radius = Int(0)

    def open_dialog(self, sensors):
        """Opens a dialog to set the sensors.

        :param sensors: Already defined sensors
        :type sensors: List(Sensor)
        :returns: Defined sensors
        :rtype: List(Sensor)
        """
        self.sensors = sensors
        self.update_storage_properties()
        self.fname = self.images[self.cur_image_number]
        self.ref_image = ImageResource(
            join(travel_sensor_draw_images_dir, self.fname))
        self.configure_traits(kind="livemodal")
        return self.sensors

    def update_storage_properties(self):
        self.images = get_all_files(images_dir)
        self.max_image_number = len(self.images)
        n = len(get_all_files(travel_sensor_draw_images_dir))
        if not n == self.max_image_number:
            self.set_images()

    def set_images(self):
        displacement = get_all_files(displacement_u_dir)[0]
        w, h = loadtxt(
            join(displacement_u_dir, displacement), delimiter=',').shape[:2]
        image_shape = (h, w)
        for img_name in self.images:
            img = imread(join(images_dir, img_name))
            img = resize(img, image_shape)
            imwrite(join(travel_sensor_images_dir, img_name), img)
            imwrite(join(travel_sensor_draw_images_dir, img_name), img)

    def reset_images(self):
        for img_name in self.images:
            img = imread(join(travel_sensor_images_dir, img_name))
            imwrite(join(travel_sensor_draw_images_dir, img_name), img)
        self.ref_image = ImageResource(
            join(travel_sensor_draw_images_dir, self.fname))

    def update_images(self, sensors=None):
        try:
            if sensors != None:
                del self.sensors[:]
                for s in sensors:
                    self.sensors.append(s)
            udisplacements = get_all_files(displacement_u_dir)
            vdisplacements = get_all_files(displacement_v_dir)
            progress = ProcessDialog(
                max_n=self.max_image_number, title="Update")
            for i in range(self.max_image_number):
                img_name = self.images[i]
                progress.update(i, msg="Update image: {0}".format(img_name))
                udisp = loadtxt(join(displacement_u_dir, udisplacements[i]),
                                delimiter=',')
                vdisp = loadtxt(join(displacement_v_dir, vdisplacements[i]),
                                delimiter=',')
                img = imread(join(travel_sensor_images_dir, img_name))
                for t in self.sensors:
                    p1, p2 = t.points
                    x1, y1 = p1
                    x2, y2 = p2
                    u1, u2 = udisp[y1, x1], udisp[y2, x2]
                    v1, v2 = vdisp[y1, x1], vdisp[y2, x2]
                    img = self.sensor_draw.draw_travel_sensor(
                        img, t, u1, u2, v1, v2)
                imwrite(join(travel_sensor_draw_images_dir, img_name), img)
            self.ref_image = ImageResource(
                join(travel_sensor_draw_images_dir, self.fname))
        except Exception:
            dialog = ErrorDialogs()
            dialog.open_error("Some files are missing")
        progress.close()

    #=========================================================================
    # Traitsview + Traitsevents
    #=========================================================================

    ref_image = Image()

    add_btn = Button("Add travel-sensor")

    reset_btn = Button("Reset")

    button_next = Button('Next')

    button_previous = Button('Previous')

    def _reset_btn_fired(self):
        self.reset_images()
        del self.sensors[:]

    def _add_btn_fired(self):
        self.sensor_draw.draw(
            join(travel_sensor_draw_images_dir, self.fname))
        points = self.sensor_draw.points
        name = 'Sensor-{0}'.format(len(self.sensors))
        t = Sensor(name, points)
        t.radius = self.radius
        self.sensors.append(t)
        self.update_images()

    def _button_next_fired(self):
        self.cur_image_number += 1

    def _button_previous_fired(self):
        self.cur_image_number -= 1

    def _cur_image_number_changed(self):
        if self.cur_image_number >= self.max_image_number:
            self.cur_image_number = self.max_image_number - 1
        elif self.cur_image_number < 0:
            self.cur_image_number = 0
        self.fname = self.images[self.cur_image_number]
        self.ref_image = ImageResource(
            join(travel_sensor_draw_images_dir, self.fname))

    def _radius_changed(self):
        for t in self.sensors:
            t.radius = self.radius
        self.update_images()

    icon = Image(ImageResource("../../icons/smrc_icon.png"))

    smrc = Str("SmartRecord")

    view = View(
        VGroup(
            HGroup(
                UItem('smrc',
                      style_sheet="*{font: bold; font-size:32px;\
                              color:" + toolbar_background + ";}",
                      style='readonly'),
                UItem('icon')
            ),
            HGroup(
                VGroup(
                    VGroup(
                        UItem("add_btn"),
                        UItem("reset_btn"),
                    ),
                    VGroup(
                        UItem('radius'),
                        label='Radius [Subsets]:'
                    ),
                ),
                VGroup(
                    UItem('fname', style='readonly'),
                    UItem('ref_image'),
                    HGroup(
                        Item('cur_image_number', label='Image:'),
                        UItem('button_previous',
                              enabled_when='cur_image_number>0'),
                        UItem('button_next',
                              enabled_when='cur_image_number<max_image_number-1'),
                    )
                )
            ),
        ),
        title="Define regions of interest",
        handler=SensorHandler(),
        icon=ImageResource("../../../../icons/smrc_icon.png")
    )
