"""
.. module: correlation_methods
.. moduleauthor: Marcel Kennert
"""
from os.path import join

from numpy import loadtxt, nonzero
from traits.api import HasTraits, Bool, Int, Instance, Button, List
from traitsui.api import View, UItem, Item

from application.configuration import \
    displacement_u_dir, displacement_v_dir, \
    strain_exx_dir, strain_exy_dir, strain_eyy_dir, \
    travel_sensor_name, travel_sensor_sensors_dir
from basic_modules.basic_classes import Combobox
from basic_modules.basic_dialogs import ProcessDialog, ErrorDialogs
from basic_modules.basic_methods import get_all_files, clear_folder
from experiment.correlation.methods.sensor import \
    SensorDialog, Sensor


class ICorrelate(HasTraits):
    """Base class for the correlation-methods."""

    show = Bool(True)

    def correlate_all_images(self):
        """Correlates all images with the specific method."""
        raise NotImplementedError()


class SensorMethod(ICorrelate):
    """Method to set travel-sensors and correlate them."""

    sensors = List(Sensor)

    sensor_dialog = Instance(SensorDialog, ())

    number_of_sensors = Int(2)

    horizontal = Bool()

    options = Instance(Combobox, ())

    def __init__(self):
        self.options.add_item('automatically', None)
        self.options.add_item('manually', None)
        self.options.selected_key = 'manually'
        self.options.add_listener(self)
        self.show = True
        files = get_all_files(travel_sensor_sensors_dir)
        for f in files:
            if ".npy" in f:
                sensor = Sensor.load(join(travel_sensor_sensors_dir, f), False)
                self.sensors.append(sensor)

    def correlate_all_images(self):
        """Positions all sensors and correlate them."""
        if not self.manually:
            self.sensors = self.create_sensors()
            self.sensor_dialog.update_storage_properties()
            self.sensor_dialog.update_images(self.sensors)
        self.correlate(self.sensors)

    def correlate(self, travel_sensors):
        """Correlates the travel-sensors.

        :param travel_sensors: All travel-sensors.
        :type travel_sensors: List(Sensor) 
        """
        try:
            udisplacements = get_all_files(displacement_u_dir)
            vdisplacements = get_all_files(displacement_v_dir)
            strain_exx = get_all_files(strain_exx_dir)
            strain_exy = get_all_files(strain_exy_dir)
            strain_eyy = get_all_files(strain_eyy_dir)
            n = len(strain_exx)
            progress = ProcessDialog(title="Calculate values", max_n=n)
            for i in range(n):
                progress.update(n=i, msg="Image: {0}".format(i))
                udisp = loadtxt(join(displacement_u_dir, udisplacements[i]),
                                delimiter=',')
                vdisp = loadtxt(join(displacement_v_dir, vdisplacements[i]),
                                delimiter=',')
                sexx = loadtxt(join(strain_exx_dir, strain_exx[i]), delimiter=',')
                sexy = loadtxt(join(strain_exy_dir, strain_exy[i]), delimiter=',')
                seyy = loadtxt(join(strain_eyy_dir, strain_eyy[i]), delimiter=',')
                for j in range(len(travel_sensors)):
                    t = travel_sensors[j]
                    tvals = []
                    tvals.append(t.get_average_values(udisp))
                    tvals.append(t.get_average_values(vdisp))
                    tvals.append(t.get_average_values(sexx))
                    tvals.append(t.get_average_values(sexy))
                    tvals.append(t.get_average_values(seyy))
                    t.append_values(tvals)
            clear_folder(travel_sensor_sensors_dir)
            for t in travel_sensors:
                t.save()
        except Exception:
            dialog=ErrorDialogs()
            dialog.open_error("Some files are missing. Cancel the process")
        progress.close()
        

    def create_sensors(self):
        """Generates sensors."""
        udisp = get_all_files(displacement_u_dir)[0]
        udisp = loadtxt(join(displacement_u_dir, udisp), delimiter=',')
        rows, cols = nonzero(udisp)
        n = self.number_of_sensors
        res = []
        if self.horizontal:
            distances = self.divide_interval(rows[5], rows[-5], n)
            for i in range(len(distances)):
                dist = distances[i]
                points = [(cols[1], dist), (cols[-1], dist)]
                sensor=Sensor(travel_sensor_name.format(i), points)
                sensor.radius=1
                res.append(sensor)
        else:
            distances = self.divide_interval(cols[1], cols[-1], n)
            for i in range(len(distances)):
                dist = distances[i]
                points = [(dist, rows[1]), (dist, rows[-1])]
                sensor=Sensor(travel_sensor_name.format(i), points)
                sensor.radius=5
                res.append(sensor)
        return res

    def divide_interval(self, p1, p2, pnt_nr):
        """Divides the given interval.

        :param p1: Start-value of the interval.
        :type p1: int
        :param p2: End-value of the interval.
        :type p2: int
        :returns: The points of the interval.
        :rtype: List(int)
        """
        d = abs(p2 - p1)
        space = int(d / float(pnt_nr-1))
        arr = [p1]
        for i in range(1, pnt_nr - 1):
            arr.append(p1 + i * space)
        arr.append(p2)
        return arr

    #=========================================================================
    # Traitsview + Traitsevents
    #=========================================================================

    button_travel_sensor = Button('Set sensors')

    def _button_travel_sensor_fired(self):
        try:
            self.sensors = self.sensor_dialog.open_dialog(self.sensors)
        except Exception:
            error=ErrorDialogs()
            error.open_error("Some files are missing.")
        
    def selected_changed(self, selected):
        if selected == 'automatically':
            self.manually = False
        else:
            self.manually = True

    manually = Bool(True)

    view = View(
        Item('options', style='custom'),
        Item('number_of_sensors', visible_when='not manually'),
        Item('horizontal', visible_when='not manually'),
        UItem('button_travel_sensor', visible_when='manually')
    )

# Can be extended
all_methods = {'travel-sensor': SensorMethod()}
