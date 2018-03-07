"""
.. module: recorder
.. moduleauthor: Marcel Kennert
"""
from json import dump, load as jload
from logging import getLogger
from os.path import join

from numpy import array
from numpy import save, load
from pyface.image_resource import ImageResource
from traits.api import HasTraits, List, Instance, Bool
from traitsui.api import View, HGroup, UItem, ListStrEditor, Image
from traitsui.group import VGroup

from application.configuration import \
    resized_images_dir, recording_file,\
    recorder_dir, recorder_file, images_dir
from basic_modules.basic_classes import InstanceUItem
from basic_modules.basic_methods import \
    time_to_secs, secs_to_time, get_all_files
from camera.camera_interfaces import ICameraListener
from experiment.recorder.recording.plotview import PlotView
from experiment.recorder.recording.result_viewer import ResultViewer
from measuring_card.ports import Port


class Recorder(HasTraits, ICameraListener):
    """Container to save all records of a experiment"""

    #=========================================================================
    # Important components to interact
    #=========================================================================

    plotview = Instance(PlotView, ())

    #=========================================================================
    # Properties of the recorder
    #=========================================================================

    input_ports = List(Port)

    container = List(List)

    record_information = List()

    images = List()

    record_mode = Bool()

    logger = getLogger('Application')

    def __init__(self, record_mode):
        self.logger.debug('Initialize Recorder')
        self.record_mode = record_mode
        self.plotview.model = self
        self.result_viewer = ResultViewer(self)

    def append(self, info, rec):
        """Appends new values to the recorder.

        :param info: Values of the input ports.
        :type info: List(Float)
        :param rec: Recording time.
        :type rec: str.
        """
        pid, value = info
        for i in range(self.n):
            p = self.input_ports[i]
            if p.id == pid:
                self.container[i].append((rec, value))

    def reset(self, input_ports):
        """Reset all information of the recorder

        :param input_ports: All input ports of the measuring card
        :type input_ports: List(Port)
        """
        del self.input_ports[:]
        del self.container[:]
        del self.record_information[:]
        self.plotview.update_subplots(input_ports)
        self.n = len(input_ports)
        for i in range(self.n):
            self.input_ports.append(input_ports[i])
            self.container.append([])

    def get_values(self):
        """Returns all recorded values"""
        res = []
        for i in range(len(self.container[0])):
            row = []
            for j in range(self.n):
                rec, val = self.container[j][i]
                row.append(val)
            row.insert(0, time_to_secs(rec))
            res.append(row)
        return array(res)

    #=========================================================================
    # Update methods
    #=========================================================================

    def _update_record_information(self, index):
        """Update the record information by the given index

        :param index: Index of the values which should show
        :type index: int
        """
        self.index = index
        del self.record_information[:]
        for i in range(self.n):
            rec, val = self.container[i][index]
            label = '{0}: {1:.3f}'.format(self.input_ports[i].name, val)
            self.record_information.append(label)
        self.record_information.append('Time: {0}'.format(rec))
        if not self.show_reference:
            files = get_all_files(images_dir)
            self.update_reference(files[0])
        self.plotview.update_focus_point(index)
        self.result_viewer.update_image(index)

    def update_reference(self, f):
        """Load the reference image from the reference dir"""
        self.logger.debug("Update reference image [Recorder]")
        self.reference_image = ImageResource(join(resized_images_dir, f))
        self.show_reference = True

    def _update_plots(self):
        # Update all values with the currently values of the recorder.
        self.plotview.update_values(self.get_values())
    
    def update_image(self, index):
        self.result_viewer.show_recorded_image(index)
    #=========================================================================
    # Methods to save and load the data
    #=========================================================================

    def save(self):
        self.logger.debug("Save recorded values [Recorder]")
        Recorder.save_values(self.get_values())
        Recorder.save_images(self.images)
    
    @staticmethod
    def save_values(values):
        save(join(recorder_dir, recording_file), values)
        
    @staticmethod
    def save_images(images):
        data = {}
        data["images"] = []
        for img in images:
            data["images"].append(img)
        with open(join(recorder_dir, recorder_file), 'w') as f:
            dump(data, f, indent=2)
    
    def load(self, input_ports):
        self.logger.debug("Load recorded values [Recorder]")
        with open(join(recorder_dir, recorder_file), 'r') as f:
            data = jload(f)
        self.images = data["images"]
        values = load(join(recorder_dir, recording_file))
        self.reset(input_ports)
        nv = len(values)
        nip = len(input_ports)
        self.plotview.update_subplots(input_ports)
        self.plotview.update_values(values)
        for i in range(nv):
            t = secs_to_time(values[i, 0])
            for j in range(nip):
                self.container[j].append((t, values[i, j + 1]))
        self.result_viewer.show_images=False
        self._update_record_information(0)
        self.show_images=True
        

    #=========================================================================
    # Traitsview + Traitsevent
    #=========================================================================

    result_viewer = Instance(ResultViewer)

    scroll_able = Bool(True)

    show_images = Bool(False)

    show_reference = Bool(False)

    reference_image = Image()
    
    def _show_images_changed(self):
        self.result_viewer.show_images=self.show_images
        
    view = View(
        VGroup(
            HGroup(
                VGroup(
                    InstanceUItem('plotview', style='custom', width=400),
                    VGroup(
                        UItem('record_information',
                              editor=ListStrEditor(auto_add=False, editable=False)),
                        label="Recorded values:",
                        visible_when='show_images'
                    )
                ),
                VGroup(
                    VGroup(
                        UItem('reference_image', width=300, height=225),
                        label='Reference Image:',
                        visible_when='show_reference'
                    ),
                    VGroup(
                        UItem('result_viewer', style='custom',
                              visible_when='show_images'),
                    ),
                    layout='normal'
                ),
            )
        )
    )
