'''
Created on 22.11.2017

@author: mkennert
'''
from itertools import cycle
from logging import getLogger
from os.path import join

from PySide.QtCore import Qt
from PySide.QtGui import QMainWindow
from cv2 import imread, namedWindow, WINDOW_NORMAL, imshow,\
    waitKey, destroyAllWindows
from numpy import load
from pyface.image_resource import ImageResource
from traits.api import HasTraits, Instance, Button, Int, Bool, List, Str
from traitsui.api import Handler, UIInfo
from traitsui.api import View, Item, UItem, HGroup, VGroup, Image
from traitsui.editors.instance_editor import InstanceEditor
from traitsui.editors.list_editor import ListEditor

from application.configuration import resized_images_dir, \
    result_normal_dir, result_resized_dir,\
    strain_exx_img_file, strain_exy_img_file, strain_eyy_img_file, images_dir,\
    travel_sensor_sensors_dir, recording_file, recorder_dir, stylesheet_smrc,\
    toolbar_background
from basic_modules.basic_classes import Combobox
from basic_modules.basic_methods import \
    convert_number, get_all_files
from experiment.correlation.methods.sensor import Sensor
from experiment.recorder.recording.plotview import PlotView
from measuring_card.card import MeasuringCard


class GraphHandler(Handler):
    """Handles the interaction with the SMRCModel and the SMRCWindow."""

    # The UIInfo object associated with the view
    info = Instance(UIInfo)

    def init(self, info):
        info.ui.control.setContextMenuPolicy(Qt.NoContextMenu)
        for c in info.ui.control.children():
            if isinstance(c, QMainWindow):
                c.setContextMenuPolicy(Qt.NoContextMenu)
        info.ui.control.setStyleSheet(stylesheet_smrc)


class TravelsensorGraph(HasTraits):

    plotview = Instance(PlotView, ())

    checkable_sensors = List()

    cycol = cycle('bgrcmky')

    force = []

    x_axis = Instance(Combobox, ())

    y_axis = Instance(Combobox, ())

    def update_sensors(self, sensors):
        del self.checkable_sensors[:]
        for s in sensors:
            c = next(self.cycol)
            s.parent = self
            s.plot_color = c
            self.checkable_sensors.append(s)

    def plot(self, index):
        self.update_axis_properties()
        self.update_plot()
        self.configure_traits()

    def get_recorded_values(self, axis):
        res = []
        for i in range(len(self.recorded_values)):
            val = self.recorded_values[i]
            if axis.selected_key == val:
                arr = load(join(recorder_dir, recording_file))
                res.append((None, arr[:, i]))
                return res

    def get_dic_values(self, axis):
        res = []
        for i in range(len(self.dic_properties)):
            val = self.dic_properties[i]
            if axis.selected_key == val:
                for t in self.checkable_sensors:
                    if t.is_checked:
                        arr = load(
                            join(travel_sensor_sensors_dir, t.name + ".npy"))
                        res.append((t, arr[:, i]))
                return res

    def update_axis_properties(self):
        self.recorded_values = ["Time [s]"]
        ports = MeasuringCard.load_input_ports_as_dict()
        for key in ports:
            self.recorded_values.append(key)
        for val in self.recorded_values:
            self.x_axis.add_item(val, self.get_recorded_values)
            self.y_axis.add_item(val, self.get_recorded_values)
        self.dic_properties = ["U-displacement [mm]", "V-displacement [mm]",
                               "Strain exx", "Strain exy", "Strain eyy"]
        for dic in self.dic_properties:
            self.x_axis.add_item(dic, self.get_dic_values)
            self.y_axis.add_item(dic, self.get_dic_values)
        self.x_axis.selected_key = self.recorded_values[0]
        self.y_axis.selected_key = self.dic_properties[0]

    def update_plot(self):
        self.x_arr = self.x_axis.get_selected_value()(self.x_axis)
        self.y_arr = self.y_axis.get_selected_value()(self.y_axis)
        self.plotview.reset_subplots("SmartRecord")
        self.plotview.set_labels(self.x_axis.selected_key,
                                 self.y_axis.selected_key, "SmartRecord")
        for x_val in self.x_arr:
            xt, xvals = x_val
            for y_val in self.y_arr:
                yt, yvals = y_val
                if xt == None:
                    self.plotview.plot_graph(0, xvals, yvals, yt.plot_color)
                else:
                    self.plotview.plot_graph(0, xvals, yvals, xt.plot_color)

    icon = Image(ImageResource("../../../../icons/smrc_icon.png"))

    smrc = Str("SmartRecord")

    update_button = Button("Update plot")

    def _update_button_fired(self):
        self.update_plot()

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
                        Item('x_axis', style='custom'),
                        Item('y_axis', style='custom'),
                        UItem('update_button'),
                        label="Axis"
                    ),
                    VGroup(
                        UItem('checkable_sensors', style='readonly',
                              editor=ListEditor(editor=InstanceEditor(),
                                                style='custom')
                              ),
                        label='Sensors',
                    ),
                ),
                UItem('plotview', style='custom')
            )
        ),
        title="Sensors",
        resizable=True,
        handler=GraphHandler()
    )


class ResultViewer(HasTraits):

    sensor_graph = Instance(TravelsensorGraph, ())

    result_options = Instance(Combobox, ())

    show_result = Button("Show")

    show_index = Int()

    cur_image = Image()

    logger = getLogger("Application")

    def __init__(self, recorder):
        self.recorder = recorder
        self.result_options.add_item(
            'recorded_image', self.show_recorded_image)
        self.result_options.add_item('strain-exx', self.show_strain_exx)
        self.result_options.add_item('strain-exy', self.show_strain_exy)
        self.result_options.add_item('strain-eyy', self.show_strain_eyy)
        self.result_options.selected_key = 'recorded_image'

    def show_recorded_image(self, index):
        if not self.recorder.show_images:
            self.result_options.add_listener(self)
            self.recorder.show_images = True
            self.show_images = True
        try:
            fname = self.recorder.images[index]
        except IndexError:
            fname = 'None'
        self.fpath = join(images_dir, fname)
        self.cur_image = ImageResource(join(resized_images_dir, fname))

    def show_strain_exx(self, index):
        fname = strain_exx_img_file.format(convert_number(index))
        self.fpath = join(result_normal_dir, fname)
        self.cur_image = ImageResource(join(result_resized_dir, fname))

    def show_strain_exy(self, index):
        fname = strain_exy_img_file.format(convert_number(index))
        self.fpath = join(result_normal_dir, fname)
        self.cur_image = ImageResource(join(result_resized_dir, fname))

    def show_strain_eyy(self, index):
        fname = strain_eyy_img_file.format(convert_number(index))
        self.fpath = join(result_normal_dir, fname)
        self.cur_image = ImageResource(join(result_resized_dir, fname))

    def update_image(self, index):
        self.index = index
        self.result_options.get_selected_value()(index)

    def selected_changed(self, selected_key):
        for key in self.result_options.values:
            if key == selected_key:
                self.update_image(self.index)

    def _sensor_fired(self):
        files = get_all_files(travel_sensor_sensors_dir)
        sensors = []
        for f in files:
            if ".npy" in f:
                sensor = Sensor.load(join(travel_sensor_sensors_dir, f))
                sensors.append(sensor)
        self.sensor_graph.update_sensors(sensors)
        self.sensor_graph.plot(0)

    def _show_result_fired(self):
        img = imread(self.fpath)
        namedWindow('image', WINDOW_NORMAL)
        imshow('image', img)
        waitKey(0)
        destroyAllWindows()

    sensor = Button('Show Sensors')

    show_images = Bool(False)

    view = View(
        VGroup(
            VGroup(
                UItem('cur_image', width=300, height=225),
                label="Recorded image:",
            ),
            HGroup(
                UItem('result_options', style='custom'),
                UItem('show_result', label='Show details'),
                UItem('sensor'),
            ),
            visible_when='show_images'
        )
    )
